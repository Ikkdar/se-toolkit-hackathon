from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.dependencies import get_current_user
from app.models import Exam, Subject, Task, User
from app.schemas import DashboardOut

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("", response_model=DashboardOut)
def get_dashboard(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    today = date.today()
    upcoming_exam_rows = (
        db.query(Exam)
        .join(Subject, Subject.id == Exam.subject_id)
        .filter(Exam.user_id == current_user.id, Exam.exam_date >= today)
        .order_by(Exam.exam_date.asc())
        .limit(10)
        .all()
    )
    todays_task_rows = (
        db.query(Task)
        .join(Subject, Subject.id == Task.subject_id)
        .filter(Task.user_id == current_user.id, Task.due_date == today)
        .order_by(Task.id.asc())
        .all()
    )

    total_tasks = db.query(Task).filter(Task.user_id == current_user.id).count()
    completed_tasks = db.query(Task).filter(Task.user_id == current_user.id, Task.status == "done").count()
    completion_rate_percent = int((completed_tasks / total_tasks) * 100) if total_tasks else 0

    upcoming_exams = [
        {
            "id": exam.id,
            "user_id": exam.user_id,
            "subject_id": exam.subject_id,
            "title": exam.title,
            "exam_date": exam.exam_date,
            "subject_name": exam.subject.name,
        }
        for exam in upcoming_exam_rows
    ]

    todays_tasks = [
        {
            "id": task.id,
            "user_id": task.user_id,
            "subject_id": task.subject_id,
            "title": task.title,
            "due_date": task.due_date,
            "status": task.status,
            "subject_name": task.subject.name,
        }
        for task in todays_task_rows
    ]

    return DashboardOut(
        upcoming_exams=upcoming_exams,
        todays_tasks=todays_tasks,
        completion_rate_percent=completion_rate_percent,
        completed_tasks=completed_tasks,
        total_tasks=total_tasks,
    )
