# ExamPulse V1 Architecture

## Stack

- Backend: FastAPI
- Database: SQLite
- ORM: SQLAlchemy
- Frontend: React + Vite
- Auth: JWT bearer token

## Scope

- Register/Login
- Subjects CRUD
- Exams CRUD
- Tasks CRUD
- Dashboard with upcoming exams + today's tasks

## Services

- One frontend app communicates with one backend API.
- One backend API communicates with one SQLite database.
- No extra services, background jobs, bots, or analytics.
