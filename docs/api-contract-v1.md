# ExamPulse API Contract (V1)

Base URL: `http://127.0.0.1:8000`

## Auth

- `POST /auth/register`
- `POST /auth/login`

## Subjects

- `GET /subjects`
- `POST /subjects`
- `PUT /subjects/{subject_id}`
- `DELETE /subjects/{subject_id}`

## Exams

- `GET /exams`
- `POST /exams`
- `PUT /exams/{exam_id}`
- `DELETE /exams/{exam_id}`

## Tasks

- `GET /tasks`
- `POST /tasks`
- `PUT /tasks/{task_id}`
- `DELETE /tasks/{task_id}`

## Dashboard

- `GET /dashboard`
