from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.dependencies import get_current_user
from app.models import Exam, Subject, Task, User
from app.schemas import SubjectCreate, SubjectDetailOut, SubjectOut, SubjectStatsOut, SubjectUpdate

router = APIRouter(prefix="/subjects", tags=["subjects"])


def _subject_stats(db: Session, user_id: int, subject: Subject) -> SubjectStatsOut:
    total_tasks = db.query(Task).filter(Task.user_id == user_id, Task.subject_id == subject.id).count()
    done_tasks = (
        db.query(Task)
        .filter(Task.user_id == user_id, Task.subject_id == subject.id, Task.status == "done")
        .count()
    )
    upcoming_exams_count = (
        db.query(Exam)
        .filter(Exam.user_id == user_id, Exam.subject_id == subject.id, Exam.exam_date >= date.today())
        .count()
    )
    todo_tasks = max(total_tasks - done_tasks, 0)
    completion_rate_percent = int((done_tasks / total_tasks) * 100) if total_tasks else 0

    return SubjectStatsOut(
        subject_id=subject.id,
        subject_name=subject.name,
        total_tasks=total_tasks,
        done_tasks=done_tasks,
        todo_tasks=todo_tasks,
        completion_rate_percent=completion_rate_percent,
        upcoming_exams_count=upcoming_exams_count,
    )


@router.get("", response_model=list[SubjectOut])
def list_subjects(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Subject).filter(Subject.user_id == current_user.id).order_by(Subject.id.desc()).all()


@router.post("", response_model=SubjectOut, status_code=status.HTTP_201_CREATED)
def create_subject(
    payload: SubjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    subject = Subject(user_id=current_user.id, name=payload.name)
    db.add(subject)
    db.commit()
    db.refresh(subject)
    return subject


@router.put("/{subject_id}", response_model=SubjectOut)
def update_subject(
    subject_id: int,
    payload: SubjectUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    subject = db.query(Subject).filter(Subject.id == subject_id, Subject.user_id == current_user.id).first()
    if subject is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found")

    subject.name = payload.name
    db.commit()
    db.refresh(subject)
    return subject


@router.delete("/{subject_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_subject(
    subject_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    subject = db.query(Subject).filter(Subject.id == subject_id, Subject.user_id == current_user.id).first()
    if subject is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found")

    db.delete(subject)
    db.commit()
    return None


@router.get("/{subject_id}", response_model=SubjectDetailOut)
def get_subject_detail(
    subject_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    subject = db.query(Subject).filter(Subject.id == subject_id, Subject.user_id == current_user.id).first()
    if subject is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found")

    exams = (
        db.query(Exam)
        .filter(Exam.user_id == current_user.id, Exam.subject_id == subject.id)
        .order_by(Exam.exam_date.asc())
        .all()
    )
    tasks = (
        db.query(Task)
        .filter(Task.user_id == current_user.id, Task.subject_id == subject.id)
        .order_by(Task.due_date.asc())
        .all()
    )

    exam_payload = [
        {
            "id": exam.id,
            "user_id": exam.user_id,
            "subject_id": exam.subject_id,
            "title": exam.title,
            "exam_date": exam.exam_date,
            "subject_name": subject.name,
        }
        for exam in exams
    ]
    task_payload = [
        {
            "id": task.id,
            "user_id": task.user_id,
            "subject_id": task.subject_id,
            "title": task.title,
            "due_date": task.due_date,
            "status": task.status,
            "subject_name": subject.name,
        }
        for task in tasks
    ]

    return SubjectDetailOut(subject=subject, exams=exam_payload, tasks=task_payload, stats=_subject_stats(db, current_user.id, subject))


@router.get("/{subject_id}/stats", response_model=SubjectStatsOut)
def get_subject_stats(
    subject_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    subject = db.query(Subject).filter(Subject.id == subject_id, Subject.user_id == current_user.id).first()
    if subject is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found")
    return _subject_stats(db, current_user.id, subject)
