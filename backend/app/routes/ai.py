import json
import re
from datetime import date, datetime, timedelta
from typing import Optional

import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.config import settings
from app.db import get_db
from app.dependencies import get_current_user
from app.models import Exam, RevisionPlan, Subject, User
from app.schemas import RevisionPlanRequest, RevisionPlanResponse, SavedPlanItemUpdate, SavedRevisionPlanOut

router = APIRouter(prefix="/ai", tags=["ai"])


def _safe_parse_plan_tasks(raw_json: str) -> list[dict]:
    try:
        data = json.loads(raw_json)
        if isinstance(data, list):
            normalized = []
            for item in data:
                if not isinstance(item, dict):
                    continue
                if not item.get("title"):
                    continue
                normalized.append(
                    {
                        "title": str(item.get("title", "")).strip(),
                        "due_date": str(item.get("due_date", date.today())),
                        "done": bool(item.get("done", False)),
                    }
                )
            return normalized
    except json.JSONDecodeError:
        return []
    return []


def _clean_task_title(item: str, subject_name: str) -> str:
    title = str(item).strip()
    title = re.sub(r"^(day|день)\s*\d+\s*[:\-]\s*", "", title, flags=re.IGNORECASE)
    title = re.sub(r"^task\s*\d+\s*[:\-]\s*", "", title, flags=re.IGNORECASE)
    title = re.sub(r"^\d+[\).:-]\s*", "", title)
    title = title.strip()

    # Remove accidental "<subject>:" prefix to keep task titles clean in Tasks page.
    subject_prefix = f"{subject_name}:"
    if title.lower().startswith(subject_prefix.lower()):
        title = title[len(subject_prefix) :].strip()

    return title or "Revision task"


def _extract_days_from_text(request_text: str, start_date: date) -> Optional[int]:
    text = request_text or ""

    relative_patterns = [
        r"(?:in|after|within)\s+(\d{1,2})\s+days?",
        r"(?:за|через|осталось|до\s+экзамена\s+осталось)\s*(\d{1,2})\s*дн(?:я|ей)?",
        r"(\d{1,2})\s*дн(?:я|ей)?\s*(?:до\s+(?:экзамена|теста))",
    ]
    for pattern in relative_patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            try:
                return int(match.group(1))
            except ValueError:
                continue

    for pattern, parser in (
        (r"(\d{4}-\d{2}-\d{2})", lambda v: datetime.strptime(v, "%Y-%m-%d").date()),
        (r"(\d{2}\.\d{2}\.\d{4})", lambda v: datetime.strptime(v, "%d.%m.%Y").date()),
    ):
        match = re.search(pattern, text)
        if not match:
            continue
        try:
            target = parser(match.group(1))
        except ValueError:
            continue
        delta = (target - start_date).days + 1
        if delta > 0:
            return delta

    return None


def _extract_tasks_count_from_text(request_text: str) -> Optional[int]:
    text = request_text or ""
    patterns = [
        r"(\d{1,2})\s*(?:tasks?|items?)",
        r"(\d{1,2})\s*(?:задач(?:а|и|)|задани(?:е|я|й))",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            try:
                return int(match.group(1))
            except ValueError:
                continue
    return None


def _infer_days_and_tasks_count(
    request_text: str,
    start_date: date,
    upcoming_exam_date: Optional[date],
    requested_days: Optional[int],
    requested_tasks_count: Optional[int],
) -> tuple[int, int]:
    prompt_days = _extract_days_from_text(request_text, start_date)

    exam_days: Optional[int] = None
    if upcoming_exam_date:
        delta = (upcoming_exam_date - start_date).days + 1
        if delta > 0:
            exam_days = delta

    days = requested_days or prompt_days or exam_days or 7
    days = max(1, min(days, 30))

    prompt_tasks_count = _extract_tasks_count_from_text(request_text)
    if requested_tasks_count:
        tasks_count = requested_tasks_count
    elif prompt_tasks_count:
        tasks_count = prompt_tasks_count
    else:
        intensity_keywords = [
            "mock",
            "variant",
            "intensive",
            "timed",
            "пробник",
            "вариант",
            "интенсив",
            "сложн",
        ]
        is_intensive = any(word in (request_text or "").lower() for word in intensity_keywords)
        tasks_per_day = 2 if is_intensive or days <= 5 else 1
        tasks_count = days * tasks_per_day

    tasks_count = max(1, min(tasks_count, 15))
    return days, tasks_count


def _fallback_plan(request_text: str, tasks_count: int) -> list[str]:
    raw = [line.strip(" -•\t") for line in request_text.replace(";", "\n").split("\n")]
    items = [chunk for chunk in raw if len(chunk) > 2]
    defaults = [
        "Review lecture notes",
        "Solve practice problems",
        "Summarize key formulas",
        "Take a mini mock test",
        "Revise weak topics",
    ]
    if not items:
        items = defaults.copy()

    i = 0
    while len(items) < tasks_count:
        items.append(defaults[i % len(defaults)])
        i += 1

    return items[:tasks_count]


def _normalize_tasks(items: list[str], tasks_count: int) -> list[str]:
    cleaned: list[str] = []
    seen: set[str] = set()
    for raw in items:
        text = str(raw).strip(" -•\t\n")
        if not text:
            continue
        key = text.lower()
        if key in seen:
            continue
        seen.add(key)
        cleaned.append(text)
        if len(cleaned) >= tasks_count:
            break
    return cleaned[:tasks_count]


def _compute_due_offset(index: int, total_tasks: int, days: int) -> int:
    if total_tasks <= 1 or days <= 1:
        return 0
    # Spread tasks across the whole period instead of stacking at the end.
    return min(days - 1, round(index * (days - 1) / (total_tasks - 1)))


def _extract_tasks_from_response(raw_response: str, tasks_count: int) -> list[str]:
    text = (raw_response or "").strip()
    if not text:
        return []

    # 1) Exact JSON path
    try:
        data = json.loads(text)
        if isinstance(data, dict):
            return _normalize_tasks(data.get("tasks", []), tasks_count)
    except json.JSONDecodeError:
        pass

    # 2) Try to parse embedded JSON object if model returned extra prose
    start = text.find("{")
    end = text.rfind("}")
    if 0 <= start < end:
        try:
            data = json.loads(text[start : end + 1])
            if isinstance(data, dict):
                tasks = _normalize_tasks(data.get("tasks", []), tasks_count)
                if tasks:
                    return tasks
        except json.JSONDecodeError:
            pass

    # 3) Fallback: parse line-by-line bullet output
    lines = [line.strip(" -•\t\n") for line in text.splitlines()]
    return _normalize_tasks(lines, tasks_count)


def _pick_model_name(available_models: list[str]) -> Optional[str]:
    if not available_models:
        return None

    preferred = settings.ollama_model.strip()
    if preferred:
        for name in available_models:
            if name == preferred or name.startswith(preferred):
                return name

    for name in available_models:
        if name.startswith("qwen"):
            return name

    return available_models[0]


def _pick_qwen_proxy_model(available_models: list[str]) -> Optional[str]:
    if not available_models:
        return settings.qwen_proxy_model.strip() or None

    preferred = settings.qwen_proxy_model.strip()
    if preferred:
        for name in available_models:
            if name == preferred:
                return name

    for name in available_models:
        if name.startswith("coder") or name.startswith("qwen"):
            return name

    return available_models[0]


def _build_prompt(
    subject_name: str,
    request_text: str,
    tasks_count: int,
    days: int,
    start_date: date,
    upcoming_exam_date: Optional[date],
) -> str:
    exam_hint = ""
    if upcoming_exam_date is not None:
        days_left = max(1, (upcoming_exam_date - start_date).days + 1)
        exam_hint = (
            f"Upcoming exam date: {upcoming_exam_date.isoformat()} "
            f"({days_left} days left from {start_date.isoformat()}). "
        )

    return "".join(
        [
            "You are a study planner. Create a concise revision plan for a student. ",
            f"Subject: {subject_name}. ",
            f"Plan start date: {start_date.isoformat()}. ",
            exam_hint,
            f"Request: {request_text}. ",
            "Infer urgency and workload from the request text and exam timeline. ",
            "If the request mentions exam or test conditions (format, limits, topics), reflect them in tasks. ",
            "Return EXACT JSON only with this schema: {\"tasks\": [\"task 1\", \"task 2\", ...]}. ",
            f"Target around {tasks_count} tasks across about {days} days, but adapt if the request implies otherwise.",
        ]
    )


def _generate_with_qwen_proxy(
    subject_name: str,
    request_text: str,
    tasks_count: int,
    days: int,
    start_date: date,
    upcoming_exam_date: Optional[date],
) -> tuple[list[str], Optional[str]]:
    prompt = _build_prompt(subject_name, request_text, tasks_count, days, start_date, upcoming_exam_date)
    base = settings.qwen_proxy_base_url.rstrip("/")
    timeout_seconds = max(5, min(settings.llm_timeout_seconds, 60))
    timeout = httpx.Timeout(connect=2.0, read=timeout_seconds, write=5.0, pool=5.0)
    headers = {"Authorization": f"Bearer {settings.qwen_proxy_api_key}"}

    with httpx.Client(timeout=timeout, headers=headers) as client:
        try:
            models_resp = client.get(f"{base}/models")
            model_name = settings.qwen_proxy_model
            if models_resp.status_code == 200:
                models = [item.get("id", "") for item in models_resp.json().get("data", []) if item.get("id")]
                model_name = _pick_qwen_proxy_model(models) or settings.qwen_proxy_model

            payload = {
                "model": model_name,
                "messages": [
                    {"role": "system", "content": "You create revision task plans and output concise JSON."},
                    {"role": "user", "content": prompt},
                ],
                "stream": False,
                "temperature": 0.2,
                "max_tokens": 320,
                "enable_thinking": False,
            }

            for _ in range(2):
                response = client.post(f"{base}/chat/completions", json=payload)
                if response.status_code in (429,) or response.status_code >= 500:
                    continue
                if response.status_code >= 400:
                    return [], model_name

                data = response.json()
                choices = data.get("choices", [])
                if not choices:
                    return [], model_name

                message = choices[0].get("message", {})
                content = message.get("content", "")
                if isinstance(content, list):
                    content = "\n".join(
                        part.get("text", "") if isinstance(part, dict) else str(part)
                        for part in content
                    )

                tasks = _extract_tasks_from_response(str(content), tasks_count)
                if tasks:
                    return tasks, model_name

            return [], model_name
        except Exception:
            return [], None


def _generate_with_qwen(
    subject_name: str,
    request_text: str,
    tasks_count: int,
    days: int,
    start_date: date,
    upcoming_exam_date: Optional[date],
) -> tuple[list[str], Optional[str]]:
    prompt = _build_prompt(subject_name, request_text, tasks_count, days, start_date, upcoming_exam_date)

    base = settings.ollama_base_url.rstrip("/")
    bounded_timeout = max(3, min(settings.ollama_timeout_seconds, 15))
    timeout = httpx.Timeout(connect=2.0, read=bounded_timeout, write=5.0, pool=5.0)

    with httpx.Client(timeout=timeout) as client:
        try:
            tags_resp = client.get(f"{base}/api/tags")
            if tags_resp.status_code != 200:
                return [], None
            models = [item.get("name", "") for item in tags_resp.json().get("models", []) if item.get("name")]
            model_name = _pick_model_name(models)
            if not model_name:
                return [], None

            for _ in range(2):
                response = client.post(
                    f"{base}/api/generate",
                    json={
                        "model": model_name,
                        "prompt": prompt,
                        "stream": False,
                        "format": "json",
                    },
                )
                if response.status_code >= 500:
                    continue
                if response.status_code >= 400:
                    return [], model_name

                text = response.json().get("response", "")
                tasks = _extract_tasks_from_response(text, tasks_count)
                if tasks:
                    return tasks, model_name

            return [], model_name
        except Exception:
            return [], None


@router.post("/revision-plan", response_model=RevisionPlanResponse, status_code=status.HTTP_201_CREATED)
def generate_revision_plan(
    payload: RevisionPlanRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    subject = db.query(Subject).filter(Subject.id == payload.subject_id, Subject.user_id == current_user.id).first()
    if subject is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid subject_id")

    start_date = payload.start_date or date.today()
    upcoming_exam = (
        db.query(Exam)
        .filter(
            Exam.user_id == current_user.id,
            Exam.subject_id == subject.id,
            Exam.exam_date >= start_date,
        )
        .order_by(Exam.exam_date.asc())
        .first()
    )
    upcoming_exam_date = upcoming_exam.exam_date if upcoming_exam is not None else None

    days, tasks_count = _infer_days_and_tasks_count(
        request_text=payload.request_text,
        start_date=start_date,
        upcoming_exam_date=upcoming_exam_date,
        requested_days=payload.days,
        requested_tasks_count=payload.tasks_count,
    )

    plan_items: list[str] = []
    model_used: Optional[str] = None
    provider_used: Optional[str] = None

    provider = settings.llm_provider.strip().lower()
    if provider in ("auto", "qwen_proxy"):
        plan_items, model_used = _generate_with_qwen_proxy(
            subject.name,
            payload.request_text,
            tasks_count,
            days,
            start_date,
            upcoming_exam_date,
        )
        if plan_items:
            provider_used = "qwen-code-api"

    if not plan_items and provider in ("auto", "ollama"):
        plan_items, model_used = _generate_with_qwen(
            subject.name,
            payload.request_text,
            tasks_count,
            days,
            start_date,
            upcoming_exam_date,
        )
        if plan_items:
            provider_used = "ollama"

    if not plan_items:
        plan_items = _fallback_plan(payload.request_text, tasks_count)
        provider_used = "fallback"
        model_used = "fallback"

    generated_tasks = []
    for index, item in enumerate(plan_items):
        due_offset = _compute_due_offset(index, len(plan_items), days)
        clean_title = _clean_task_title(item, subject.name)
        generated_tasks.append(
            {
                "title": clean_title,
                "due_date": start_date + timedelta(days=due_offset),
                "done": False,
            }
        )

    summary_text = f"Generated {len(generated_tasks)} revision tasks for {subject.name}."

    plan_snapshot = [
        {
            "title": task["title"],
            "due_date": str(task["due_date"]),
            "done": bool(task.get("done", False)),
        }
        for task in generated_tasks
    ]
    plan_record = RevisionPlan(
        user_id=current_user.id,
        subject_id=subject.id,
        request_text=payload.request_text,
        summary=summary_text,
        provider=provider_used or "fallback",
        model_name=model_used or "fallback",
        start_date=start_date,
        days=days,
        tasks_count=tasks_count,
        generated_tasks_json=json.dumps(plan_snapshot),
    )
    db.add(plan_record)

    db.commit()

    return RevisionPlanResponse(
        subject_id=subject.id,
        generated_tasks=[
            {
                "title": task["title"],
                "due_date": task["due_date"],
                "done": bool(task.get("done", False)),
            }
            for task in generated_tasks
        ],
        summary=summary_text,
    )


@router.get("/plans", response_model=list[SavedRevisionPlanOut])
def list_saved_revision_plans(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    rows = (
        db.query(RevisionPlan)
        .join(Subject, Subject.id == RevisionPlan.subject_id)
        .filter(RevisionPlan.user_id == current_user.id)
        .order_by(RevisionPlan.created_at.desc())
        .limit(100)
        .all()
    )

    return [
        {
            "id": row.id,
            "subject_id": row.subject_id,
            "subject_name": row.subject.name,
            "request_text": row.request_text,
            "summary": row.summary,
            "provider": row.provider,
            "model_name": row.model_name,
            "start_date": row.start_date,
            "days": row.days,
            "tasks_count": row.tasks_count,
            "generated_tasks": _safe_parse_plan_tasks(row.generated_tasks_json),
            "created_at": row.created_at,
        }
        for row in rows
    ]


@router.delete("/plans/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_saved_revision_plan(
    plan_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    row = db.query(RevisionPlan).filter(RevisionPlan.id == plan_id, RevisionPlan.user_id == current_user.id).first()
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found")

    db.delete(row)
    db.commit()
    return None


@router.patch("/plans/{plan_id}/items/{item_index}", response_model=SavedRevisionPlanOut)
def update_saved_plan_item(
    plan_id: int,
    item_index: int,
    payload: SavedPlanItemUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    row = db.query(RevisionPlan).filter(RevisionPlan.id == plan_id, RevisionPlan.user_id == current_user.id).first()
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found")

    items = _safe_parse_plan_tasks(row.generated_tasks_json)
    if item_index < 0 or item_index >= len(items):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan item not found")

    items[item_index]["done"] = payload.done
    row.generated_tasks_json = json.dumps(items)
    db.commit()
    db.refresh(row)

    return {
        "id": row.id,
        "subject_id": row.subject_id,
        "subject_name": row.subject.name,
        "request_text": row.request_text,
        "summary": row.summary,
        "provider": row.provider,
        "model_name": row.model_name,
        "start_date": row.start_date,
        "days": row.days,
        "tasks_count": row.tasks_count,
        "generated_tasks": _safe_parse_plan_tasks(row.generated_tasks_json),
        "created_at": row.created_at,
    }
