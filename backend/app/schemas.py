from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SubjectCreate(BaseModel):
    name: str


class SubjectUpdate(BaseModel):
    name: str


class SubjectOut(BaseModel):
    id: int
    user_id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class ExamCreate(BaseModel):
    subject_id: int
    title: str
    exam_date: date


class ExamUpdate(BaseModel):
    subject_id: int
    title: str
    exam_date: date


class ExamOut(BaseModel):
    id: int
    user_id: int
    subject_id: int
    title: str
    exam_date: date

    model_config = ConfigDict(from_attributes=True)


class TaskCreate(BaseModel):
    subject_id: int
    title: str
    due_date: date
    status: Literal["todo", "done"] = "todo"


class TaskUpdate(BaseModel):
    subject_id: int
    title: str
    due_date: date
    status: Literal["todo", "done"]


class TaskOut(BaseModel):
    id: int
    user_id: int
    subject_id: int
    title: str
    due_date: date
    status: Literal["todo", "done"]

    model_config = ConfigDict(from_attributes=True)


class DashboardOut(BaseModel):
    upcoming_exams: list[ExamOut]
    todays_tasks: list[TaskOut]
