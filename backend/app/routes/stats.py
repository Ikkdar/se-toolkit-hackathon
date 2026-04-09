from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.dependencies import get_current_user
from app.models import Exam, Subject, Task, User
from app.schemas import StudyStatsOverviewOut, SubjectStatsOut

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("/overview", response_model=StudyStatsOverviewOut)
def stats_overview(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    subjects = db.query(Subject).filter(Subject.user_id == current_user.id).order_by(Subject.name.asc()).all()

    subject_stats: list[SubjectStatsOut] = []
    total_tasks_acc = 0
    total_done_acc = 0

    for subject in subjects:
        total_tasks = db.query(Task).filter(Task.user_id == current_user.id, Task.subject_id == subject.id).count()
        done_tasks = (
            db.query(Task)
            .filter(Task.user_id == current_user.id, Task.subject_id == subject.id, Task.status == "done")
            .count()
        )
        upcoming_exams_count = (
            db.query(Exam)
            .filter(Exam.user_id == current_user.id, Exam.subject_id == subject.id, Exam.exam_date >= date.today())
            .count()
        )

        total_tasks_acc += total_tasks
        total_done_acc += done_tasks

        subject_stats.append(
            SubjectStatsOut(
                subject_id=subject.id,
                subject_name=subject.name,
                total_tasks=total_tasks,
                done_tasks=done_tasks,
                todo_tasks=max(total_tasks - done_tasks, 0),
                completion_rate_percent=int((done_tasks / total_tasks) * 100) if total_tasks else 0,
                upcoming_exams_count=upcoming_exams_count,
            )
        )

    return StudyStatsOverviewOut(
        subjects=subject_stats,
        total_subjects=len(subject_stats),
        total_tasks=total_tasks_acc,
        total_done_tasks=total_done_acc,
        overall_completion_rate_percent=int((total_done_acc / total_tasks_acc) * 100) if total_tasks_acc else 0,
    )
