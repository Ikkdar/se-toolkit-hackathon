from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.dependencies import get_current_user
from app.models import Exam, Task, User
from app.schemas import DashboardOut

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("", response_model=DashboardOut)
def get_dashboard(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    today = date.today()
    upcoming_exams = (
        db.query(Exam)
        .filter(Exam.user_id == current_user.id, Exam.exam_date >= today)
        .order_by(Exam.exam_date.asc())
        .limit(10)
        .all()
    )
    todays_tasks = (
        db.query(Task)
        .filter(Task.user_id == current_user.id, Task.due_date == today)
        .order_by(Task.id.asc())
        .all()
    )
    return DashboardOut(upcoming_exams=upcoming_exams, todays_tasks=todays_tasks)
