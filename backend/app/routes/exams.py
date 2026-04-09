from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.dependencies import get_current_user
from app.models import Exam, Subject, User
from app.schemas import ExamCreate, ExamOut, ExamUpdate

router = APIRouter(prefix="/exams", tags=["exams"])


def _validate_user_subject(db: Session, user_id: int, subject_id: int) -> Subject:
    subject = db.query(Subject).filter(Subject.id == subject_id, Subject.user_id == user_id).first()
    if subject is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid subject_id")
    return subject


@router.get("", response_model=list[ExamOut])
def list_exams(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    exams = (
        db.query(Exam)
        .join(Subject, Subject.id == Exam.subject_id)
        .filter(Exam.user_id == current_user.id)
        .order_by(Exam.exam_date.asc())
        .all()
    )
    return [
        {
            "id": exam.id,
            "user_id": exam.user_id,
            "subject_id": exam.subject_id,
            "title": exam.title,
            "exam_date": exam.exam_date,
            "subject_name": exam.subject.name,
        }
        for exam in exams
    ]


@router.post("", response_model=ExamOut, status_code=status.HTTP_201_CREATED)
def create_exam(
    payload: ExamCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _validate_user_subject(db, current_user.id, payload.subject_id)
    exam = Exam(
        user_id=current_user.id,
        subject_id=payload.subject_id,
        title=payload.title,
        exam_date=payload.exam_date,
    )
    db.add(exam)
    db.commit()
    db.refresh(exam)
    return exam


@router.put("/{exam_id}", response_model=ExamOut)
def update_exam(
    exam_id: int,
    payload: ExamUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    exam = db.query(Exam).filter(Exam.id == exam_id, Exam.user_id == current_user.id).first()
    if exam is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exam not found")

    _validate_user_subject(db, current_user.id, payload.subject_id)
    exam.subject_id = payload.subject_id
    exam.title = payload.title
    exam.exam_date = payload.exam_date
    db.commit()
    db.refresh(exam)
    return exam


@router.delete("/{exam_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_exam(
    exam_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    exam = db.query(Exam).filter(Exam.id == exam_id, Exam.user_id == current_user.id).first()
    if exam is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exam not found")

    db.delete(exam)
    db.commit()
    return None
