from datetime import date, timedelta

from fastapi.testclient import TestClient

from app.db import Base, engine
from app.main import app


def run_smoke() -> None:
    Base.metadata.create_all(bind=engine)
    client = TestClient(app)
    email = f"student_{date.today().isoformat()}@example.com"
    password = "pass1234"

    register = client.post("/auth/register", json={"email": email, "password": password})
    assert register.status_code in (201, 400), register.text

    login = client.post("/auth/login", json={"email": email, "password": password})
    assert login.status_code == 200, login.text
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    subject = client.post("/subjects", json={"name": "Math"}, headers=headers)
    assert subject.status_code == 201, subject.text
    subject_id = subject.json()["id"]

    exam_payload = {
        "subject_id": subject_id,
        "title": "Math Midterm",
        "exam_date": (date.today() + timedelta(days=5)).isoformat(),
    }
    exam = client.post("/exams", json=exam_payload, headers=headers)
    assert exam.status_code == 201, exam.text

    task_payload = {
        "subject_id": subject_id,
        "title": "Solve 20 integrals",
        "due_date": date.today().isoformat(),
        "status": "todo",
    }
    task = client.post("/tasks", json=task_payload, headers=headers)
    assert task.status_code == 201, task.text

    dashboard = client.get("/dashboard", headers=headers)
    assert dashboard.status_code == 200, dashboard.text
    payload = dashboard.json()
    assert "upcoming_exams" in payload
    assert "todays_tasks" in payload

    print("Smoke test passed ✅")


if __name__ == "__main__":
    run_smoke()
