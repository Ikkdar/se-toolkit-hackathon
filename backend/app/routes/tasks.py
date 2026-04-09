from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.dependencies import get_current_user
from app.models import Subject, Task, User
from app.schemas import TaskCreate, TaskOut, TaskUpdate

router = APIRouter(prefix="/tasks", tags=["tasks"])


def _validate_user_subject(db: Session, user_id: int, subject_id: int) -> Subject:
    subject = db.query(Subject).filter(Subject.id == subject_id, Subject.user_id == user_id).first()
    if subject is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid subject_id")
    return subject


@router.get("", response_model=list[TaskOut])
def list_tasks(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    tasks = (
        db.query(Task)
        .join(Subject, Subject.id == Task.subject_id)
        .filter(Task.user_id == current_user.id)
        .order_by(Task.due_date.asc())
        .all()
    )
    return [
        {
            "id": task.id,
            "user_id": task.user_id,
            "subject_id": task.subject_id,
            "title": task.title,
            "due_date": task.due_date,
            "status": task.status,
            "subject_name": task.subject.name,
        }
        for task in tasks
    ]


@router.post("", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
def create_task(
    payload: TaskCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _validate_user_subject(db, current_user.id, payload.subject_id)
    task = Task(
        user_id=current_user.id,
        subject_id=payload.subject_id,
        title=payload.title,
        due_date=payload.due_date,
        status=payload.status,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.put("/{task_id}", response_model=TaskOut)
def update_task(
    task_id: int,
    payload: TaskUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == current_user.id).first()
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    _validate_user_subject(db, current_user.id, payload.subject_id)
    task.subject_id = payload.subject_id
    task.title = payload.title
    task.due_date = payload.due_date
    task.status = payload.status
    db.commit()
    db.refresh(task)
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == current_user.id).first()
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    db.delete(task)
    db.commit()
    return None
