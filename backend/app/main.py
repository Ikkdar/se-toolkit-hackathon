from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.db import Base, engine
from app.routes.auth import router as auth_router
from app.routes.dashboard import router as dashboard_router
from app.routes.exams import router as exams_router
from app.routes.subjects import router as subjects_router
from app.routes.tasks import router as tasks_router

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)


@app.get("/")
def healthcheck():
    return {"status": "ok", "service": "ExamPulse API"}


app.include_router(auth_router)
app.include_router(subjects_router)
app.include_router(exams_router)
app.include_router(tasks_router)
app.include_router(dashboard_router)
