from datetime import date, datetime
from typing import List, Literal, Optional

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
    subject_name: Optional[str] = None

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
    subject_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class DashboardOut(BaseModel):
    upcoming_exams: list[ExamOut]
    todays_tasks: list[TaskOut]
    completion_rate_percent: int
    completed_tasks: int
    total_tasks: int


class SubjectStatsOut(BaseModel):
    subject_id: int
    subject_name: str
    total_tasks: int
    done_tasks: int
    todo_tasks: int
    completion_rate_percent: int
    upcoming_exams_count: int


class SubjectDetailOut(BaseModel):
    subject: SubjectOut
    exams: List[ExamOut]
    tasks: List[TaskOut]
    stats: SubjectStatsOut


class StudyStatsOverviewOut(BaseModel):
    subjects: List[SubjectStatsOut]
    total_subjects: int
    total_tasks: int
    total_done_tasks: int
    overall_completion_rate_percent: int


class RevisionPlanRequest(BaseModel):
    subject_id: int
    request_text: str
    start_date: Optional[date] = None
    days: int = 7
    tasks_count: int = 5


class GeneratedPlanTaskOut(BaseModel):
    title: str
    due_date: date
    done: bool = False


class RevisionPlanResponse(BaseModel):
    subject_id: int
    generated_tasks: List[GeneratedPlanTaskOut]
    summary: str


class SavedPlanTaskOut(BaseModel):
    title: str
    due_date: date
    done: bool = False


class SavedPlanItemUpdate(BaseModel):
    done: bool


class SavedRevisionPlanOut(BaseModel):
    id: int
    subject_id: int
    subject_name: str
    request_text: str
    summary: str
    provider: str
    model_name: str
    start_date: date
    days: int
    tasks_count: int
    generated_tasks: List[SavedPlanTaskOut]
    created_at: datetime
