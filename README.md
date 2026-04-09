# ExamPulse

Web-based exam preparation tracker for students.

## Demo

### Dashboard (progress, exams, tasks)

![Dashboard](docs/screenshots/dashboard-overview.png)

### Calendar view

![Calendar view](docs/screenshots/calendar-view.png)

### Plans page (LLM plan history)

![Plans page](docs/screenshots/plans-page.png)

## Project description

ExamPulse helps students plan exam preparation in a simple flow: register, add subjects, add exams, add tasks, and check what to study today.

## Product context

- End user: students preparing for exams
- Problem: exam preparation is often chaotic and unstructured
- V1 solution: one clean planner with auth + subjects + exams + tasks + dashboard

## Implemented features (V2)

- User registration and login (JWT auth)
- Subject CRUD
- Exam CRUD
- Task CRUD (`todo` / `done`)
- Dashboard with upcoming exams and today’s tasks
- AI revision planner (Qwen via Ollama) that generates and saves tasks
- Local Docker Compose setup

## Not yet implemented features

- Notifications/reminders
- Telegram bot integration
- Background jobs and async workers
- Multi-user collaboration/study groups

## Scope boundaries (current)

- Included: backend + frontend + SQLite + Docker local run + Qwen-based study plan generation
- Not included: Telegram bot, notifications, background jobs

## Section 1: Architecture

ExamPulse V1 uses a simple 3-layer architecture:

- **Frontend (`React + Vite`)**: pages for auth, CRUD flows, and dashboard.
- **Backend (`FastAPI`)**: REST API, validation, auth, business logic.
- **Database (`SQLite + SQLAlchemy`)**: persistence for users, subjects, exams, tasks.

### Version 1 boundaries

- Included: auth, subjects, exams, tasks, dashboard, Docker local run.
- Excluded: AI, bots, advanced analytics, notifications, background jobs.

### Data flow

1. Frontend sends HTTP request to backend.
2. Backend validates token + payload.
3. Backend reads/writes SQLite via SQLAlchemy.
4. Backend returns JSON response.
5. Frontend updates UI state.

For containerized local development:

- `frontend` container serves built React app (Nginx)
- `backend` container serves FastAPI API
- SQLite DB file is stored in Docker volume (`backend_data`)

## Section 2: Folder structure

```text
se-toolkit-hackathon/
├── backend/
│   ├── requirements.txt
│   ├── .env.example
│   ├── smoke_test.py
│   └── app/
│       ├── __init__.py
│       ├── config.py
│       ├── db.py
│       ├── models.py
│       ├── schemas.py
│       ├── security.py
│       ├── dependencies.py
│       ├── main.py
│       └── routes/
│           ├── auth.py
│           ├── subjects.py
│           ├── exams.py
│           ├── tasks.py
│           └── dashboard.py
├── frontend/
│   ├── package.json
│   ├── vite.config.js
│   ├── index.html
│   ├── .env.example
│   └── src/
│       ├── main.jsx
│       ├── App.jsx
│       ├── styles.css
│       ├── api/
│       │   ├── client.js
│       │   ├── authApi.js
│       │   ├── subjectsApi.js
│       │   ├── examsApi.js
│       │   ├── tasksApi.js
│       │   └── dashboardApi.js
│       ├── components/
│       │   ├── Layout.jsx
│       │   └── ProtectedRoute.jsx
│       ├── context/
│       │   └── AuthContext.jsx
│       └── pages/
│           ├── LoginPage.jsx
│           ├── RegisterPage.jsx
│           ├── DashboardPage.jsx
│           ├── SubjectsPage.jsx
│           ├── ExamsPage.jsx
│           └── TasksPage.jsx
└── docs/
    ├── architecture.md
    └── api-contract-v1.md
```

## Section 3: Backend implementation

### Database entities

- **User**: `id`, `email`, `password_hash`, `created_at`
- **Subject**: `id`, `user_id`, `name`
- **Exam**: `id`, `user_id`, `subject_id`, `title`, `exam_date`
- **Task**: `id`, `user_id`, `subject_id`, `title`, `due_date`, `status` (`todo|done`)

### API endpoints (V1)

Auth:

- `POST /auth/register`
- `POST /auth/login`

Subjects:

- `GET /subjects`
- `POST /subjects`
- `PUT /subjects/{id}`
- `DELETE /subjects/{id}`

Exams:

- `GET /exams`
- `POST /exams`
- `PUT /exams/{id}`
- `DELETE /exams/{id}`

Tasks:

- `GET /tasks`
- `POST /tasks`
- `PUT /tasks/{id}`
- `DELETE /tasks/{id}`

Dashboard:

- `GET /dashboard` (upcoming exams + today’s tasks)

## Section 4: Frontend implementation

Pages:

- `/login`
- `/register`
- `/dashboard`
- `/subjects`
- `/exams`
- `/tasks`

Core frontend behavior:

- token-based auth stored in `localStorage`
- protected routes for app pages
- forms for create flows
- list rendering for subjects/exams/tasks
- dashboard cards for upcoming exams and today’s tasks

## Usage

1. Register a new user on `/register`.
2. Login on `/login`.
3. Create subjects on `/subjects`.
4. Add exams on `/exams` and tasks on `/tasks`.
5. Open `/dashboard` to view calendar, upcoming exams, and progress.
6. Open `/planner` to generate an AI plan and `/plans` to track plan items.

## Section 5: Run instructions

### Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend default API URL: `http://127.0.0.1:8000`.

## Section 6: Docker

Created files:

- `backend/Dockerfile`
- `frontend/Dockerfile`
- `frontend/nginx.conf`
- `docker-compose.yml`

### Docker setup and run

```bash
docker compose up --build
```

After startup:

- Frontend: `http://localhost:5173`
- Backend API: `http://localhost:8000`
- API docs: `http://localhost:8000/docs`

### Qwen model setup (one-time, Ollama option)

AI planner endpoint uses Ollama + Qwen (`qwen2.5:3b`). After containers are up, pull the model:

```bash
docker exec -it exampulse-ollama ollama pull qwen2.5:3b
```

Then use `POST /ai/revision-plan` or open the frontend `AI Planner` page.

### Qwen Code API proxy integration (recommended for VM)

This project now supports `inno-se-toolkit/qwen-code-api` (OpenAI-compatible).

1. Run the proxy from that repository and make sure it responds on `http://localhost:8080/v1`.
1. Configure backend env (`backend/.env.example` values or your real `.env`):

```bash
LLM_PROVIDER=qwen_proxy
QWEN_PROXY_BASE_URL=http://localhost:8080/v1
QWEN_PROXY_API_KEY=fake-key
QWEN_PROXY_MODEL=coder-model
```

1. Restart backend service.

`LLM_PROVIDER=auto` is also supported (tries `qwen-code-api` first, then Ollama, then local fallback planner).

To stop containers:

```bash
docker compose down
```

To stop and remove DB volume:

```bash
docker compose down -v
```

## Deployment (Ubuntu 24.04 VM)

Target VM OS: **Ubuntu 24.04 LTS**.

### What should be installed on the VM

- `git`
- `docker` and `docker compose` plugin
- (optional) `curl` for health checks

### Step-by-step deployment instructions

1. Clone repository:

```bash
git clone https://github.com/Ikkdar/se-toolkit-hackathon.git
cd se-toolkit-hackathon
```

1. Start all services:

```bash
docker compose up -d --build
```

1. (Optional) Authenticate Qwen OAuth on VM host (for qwen-code-api):

```bash
qwen auth qwen-oauth
docker compose restart qwen-proxy backend
```

1. Verify services:

```bash
docker compose ps
```

1. Open the app:

- Frontend: `http://<VM_IP>:5173`
- Backend API docs: `http://<VM_IP>:8000/docs`

1. Stop services when needed:

```bash
docker compose down
```

## Section 7: Testing checklist

Main user flow checklist:

1. Register a new user via `/register` page.
2. Login via `/login` page.
3. Create at least one subject on `/subjects`.
4. Create an upcoming exam on `/exams`.
5. Create tasks (including one with today’s date) on `/tasks`.
6. Open `/dashboard` and verify:
   - upcoming exams are listed
   - today’s tasks are listed

Optional backend smoke check:

```bash
cd backend
source .venv/bin/activate
python smoke_test.py
```
