# DevPath

A 12-month learning roadmap and progress tracker for becoming a **Backend + DevOps
Engineer with Java and Spring Boot**, with a **parallel DSA interview track**. DevPath
turns a 7-phase, 69-topic core curriculum plus 2 DSA phases (24 topics) into a daily
workflow: plan study tasks, log real study time, work through projects, and watch
progress, streaks and study hours update from persisted data. The DSA track can be
paused during exams without losing any progress.

The repository contains a complete application:

- `frontend/` — React 19 + Vite + TypeScript SPA (Tailwind CSS v4, Lucide, Recharts)
- `backend/` — FastAPI + SQLAlchemy 2.0 + PostgreSQL API with JWT auth and Alembic
- `docker-compose.yml` — PostgreSQL, API and nginx-served frontend

---

## Highlights

- **6 app pages** — Dashboard, Roadmap, Daily Planner, Project Tracker, Resources,
  Settings — plus login/register.
- **7 phases / 69 topics** of a Backend + DevOps curriculum, plus a parallel
  **2-phase / 24-topic DSA interview track**, seeded once and shared by every account.
- **Exam pause** — pause the DSA track indefinitely or until a resume date; progress is
  preserved and a paused track is excluded from active dashboard goals.
- **6 prepopulated projects** (with milestones and checklists) scaffolded for each
  new learner.
- **Derived progress** — completion percentages, study hours and streaks are always
  computed from persisted records. Re-completing a topic or reloading a page never
  double-counts anything.
- **Per-user ownership** — every task, note, checklist item, project, bookmark,
  preference and progress row belongs to the authenticated user. User IDs are taken
  from the JWT, never from request bodies.
- **Real study logging** — `study_sessions` is the single source of truth for study
  hours; logging time against a task keeps one idempotent session in sync.
- **30 verified resources** (official Java, Spring, PostgreSQL, Docker, Kubernetes,
  AWS, Linux, Git, CI/CD documentation) plus private custom resources.
- **Settings** — profile, password change, daily goal, theme, reminders, JSON/CSV
  export, validated import and a confirmed progress reset.
- **Light/dark themes**, responsive sidebar + mobile navigation, skeletons, empty
  states and keyboard-accessible forms and dialogs.
- **Automated tests** — 102 Pytest tests and 29 Vitest/Testing Library tests, plus an
  end-to-end script that runs real migrations against PostgreSQL.

---

## Tech stack

| Layer | Technology |
|---|---|
| Frontend | React 19, Vite 6, TypeScript, Tailwind CSS v4, Lucide React, Recharts, TanStack Query v5, React Router v7 |
| Backend | Python 3.11+, FastAPI, Pydantic v2, SQLAlchemy 2.0 (sync), Alembic, psycopg 3 |
| Database | PostgreSQL 16 |
| Auth | bcrypt password hashing, PyJWT access tokens, rotating opaque refresh tokens (stored as SHA-256 digests) |
| Tests | Pytest, Starlette TestClient, Vitest, Testing Library, jsdom |
| Runtime | Docker Compose (PostgreSQL + uvicorn + nginx) |

---

## Repository layout

```text
skill-tracker/
├── backend/
│   ├── app/
│   │   ├── api/v1/          # HTTP routers (auth, roadmap, planner, projects, resources, settings, dashboard, health)
│   │   ├── core/            # settings, security, errors, logging
│   │   ├── db/              # engine/session, Base, seed data
│   │   ├── models/          # SQLAlchemy 2.0 models
│   │   ├── repositories/    # SQL queries
│   │   ├── schemas/         # Pydantic request/response contracts
│   │   ├── services/        # business rules and progress maths
│   │   ├── tests/           # Pytest suite
│   │   └── main.py          # FastAPI app factory
│   ├── alembic/versions/    # initial migration
│   ├── scripts/e2e_check.py # end-to-end verification against PostgreSQL
│   ├── Dockerfile · requirements.txt · requirements-dev.txt · alembic.ini · .env.example
├── frontend/
│   ├── src/
│   │   ├── api/             # fetch client, typed endpoints, TanStack Query hooks
│   │   ├── components/      # layout, common and UI primitives
│   │   ├── contexts/        # auth, theme, toasts
│   │   ├── pages/           # the 6 pages + auth pages + 404
│   │   ├── lib/             # formatting, errors, constants, page title
│   │   └── types/           # shared API types
│   ├── Dockerfile · nginx.conf · vite.config.ts · package.json
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## Quick start with Docker Compose

Requirements: Docker Desktop (or Docker Engine + Compose v2).

```bash
cp .env.example .env
# Set a strong SECRET_KEY in .env before exposing the app.
docker compose up --build
```

Then open:

| Service | URL |
|---|---|
| App | http://localhost:5173 |
| API | http://localhost:8000 |
| Swagger UI | http://localhost:8000/docs |
| ReDoc | http://localhost:8000/redoc |
| Health (liveness) | http://localhost:8000/api/v1/health |
| Health (readiness) | http://localhost:8000/api/v1/health/ready |

The API container runs `alembic upgrade head` before starting uvicorn, and
`SEED_ON_STARTUP=true` seeds the shared roadmap, resources and the demo account
idempotently.

**Demo account**

```text
email:    demo@devpath.dev
password: devpath-demo-123
```

The demo account comes with sample progress, tasks, sessions and project activity so
the dashboard is not empty on first login.

To stop and remove everything, including the database volume:

```bash
docker compose down -v
```

---

## Local development

### Prerequisites

- Python 3.11+ (3.12 recommended)
- Node.js 20+ (24 used during development)
- PostgreSQL 16 running locally, with a database and user for DevPath

### 1. Backend

```bash
cd backend
python -m venv .venv
```

Activate the virtual environment:

```powershell
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
```

```bash
# macOS / Linux
source .venv/bin/activate
```

Install dependencies and configure the environment:

```bash
pip install -r requirements-dev.txt
cp .env.example .env
```

`requirements.txt` contains runtime dependencies only (used by the Docker image);
`requirements-dev.txt` adds pytest, httpx, ruff and the embedded PostgreSQL used by
the tests.

Edit `backend/.env`:

```dotenv
DATABASE_URL=postgresql+psycopg://devpath:devpath@localhost:5432/devpath
SECRET_KEY=<a long random string>
```

Generate a key with:

```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Create the schema and seed data:

```bash
alembic upgrade head
python -m app.db.seed            # shared roadmap + demo account
# or: python -m app.db.seed --no-demo
```

Run the API:

```bash
uvicorn app.main:app --reload --port 8000
```

### 2. Frontend

In a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173. The Vite dev server proxies `/api` to
`http://localhost:8000` by default; override it with `VITE_PROXY_TARGET`.

To point the built app at a different API origin, set `VITE_API_URL` (for example
`https://api.example.com/api/v1`) before `npm run build`. It is inlined at build
time. When served by the bundled nginx config, keep it as `/api/v1`.

---

## Pages

| Page | What it does |
|---|---|
| **Dashboard** | Overall/phase progress, a separate DSA track summary card (with paused state), current and longest streak, study totals, weekly study chart, today's tasks, next topic and project summary. |
| **Roadmap** | Core (seven phases) and parallel DSA (two phases) with a track switcher, topic status, priority, completion percentages, pause/resume controls and per-track links. |
| **Topic detail** | Mark a topic not started / in progress / completed, rate it, take notes and manage a personal checklist. Previous/next topic navigation. |
| **Daily Planner** | Day view with planned vs completed work, task CRUD, completion toggle, carry-forward, study-session logging, calendar and weekly summary. |
| **Project Tracker** | Six seeded portfolio projects, status/priority/dates/links, milestones and checklists; completion is derived from milestones. |
| **Resources** | Searchable/filterable library of official docs and personal resources, bookmarks and optional topic linking. |
| **Settings** | Profile, password change, daily goal, theme, reminders/timezone, JSON/CSV export, validated import and confirmed reset. |

---

## API

All endpoints are versioned under `/api/v1`. Interactive documentation is available
at `/docs` (Swagger UI) and `/redoc`; the raw schema is at `/openapi.json`.

Private routes require:

```http
Authorization: Bearer <access_token>
```

| Group | Endpoints |
|---|---|
| Auth | `POST /auth/register`, `POST /auth/login`, `POST /auth/refresh`, `POST /auth/logout`, `GET/PATCH /auth/me`, `POST /auth/change-password` |
| Health | `GET /health`, `GET /health/ready` |
| Dashboard | `GET /dashboard` |
| Roadmap | `GET /roadmap/phases`, `GET /roadmap/next`, `GET /roadmap/topics/{id}`, `GET /roadmap/topics/{id}/navigation`, `PATCH /roadmap/topics/{id}/progress`, notes and checklist CRUD |
| Planner | `GET/POST /planner/tasks`, `GET/PATCH/DELETE /planner/tasks/{id}`, `PATCH /planner/tasks/{id}/completion`, `POST /planner/tasks/{id}/log`, `POST /planner/tasks/{id}/carry-forward`, sessions CRUD, `GET /planner/day`, `GET /planner/calendar`, `GET /planner/week`, `GET /planner/streak` |
| Projects | `GET/POST /projects`, `GET/PATCH/DELETE /projects/{id}`, `POST /projects/{id}/complete`, milestone and checklist CRUD, `GET /projects/summary` |
| Resources | `GET/POST /resources`, `GET /resources/categories`, `GET/PATCH/DELETE /resources/{id}`, `PUT /resources/{id}/bookmark`, `PUT /resources/{id}/link` |
| Settings | `GET/PATCH /settings`, `GET /settings/export.json`, `GET /settings/export.csv`, `POST /settings/import/validate`, `POST /settings/import`, `POST /settings/reset` |

List endpoints accept pagination where relevant (`page`, `page_size`) and return a
`meta` object with `page`, `page_size`, `total` and `pages`.

### Error format

Errors are uniform JSON:

```json
{
  "error": {
    "code": "task_not_found",
    "message": "Task not found"
  }
}
```

Validation errors use `code: "validation_error"` and add a `details.errors` array.
A `details` object is included when the error carries extra context. Every response
also carries an `X-Request-ID` header for log correlation.

---

## Data model and progress rules

Global/shared data: `roadmap_phases`, `topics`, `resources`, `topic_resources`.

Per-user data: `topic_progress`, `topic_notes`, `topic_checklist_items`,
`daily_tasks`, `study_sessions`, `projects`, `project_milestones`,
`project_checklist_items`, `user_resource_links`, `user_preferences`,
`refresh_tokens`.

- Topic progress = completed topics / total topics (overall and per phase).
- Project progress = completed milestones / total milestones.
- Study hours = `SUM(study_sessions.minutes) / 60`.
- Streak = consecutive active days, where an active day has at least one study
  session **or** a completed task with `actual_minutes > 0`.
- Re-opening a topic clears `completed_at`; re-completing sets it again. Progress is
  derived from current status, so counters can never be double-incremented.
- Logging time on a task updates the task's `actual_minutes` and upserts a single
  linked study session, so re-logging corrects the total instead of adding a duplicate.

---

## Migrations

```bash
cd backend
alembic upgrade head        # apply
alembic downgrade base      # roll everything back
alembic current             # show the applied revision
```

The e2e script verifies a full `upgrade → seed → downgrade base → upgrade → seed`
round-trip.

---

## Tests

### Backend

```bash
cd backend
pytest
```

The suite prefers a real PostgreSQL server. It uses, in order:

1. `TEST_DATABASE_URL` if set,
2. an embedded PostgreSQL started by `pgserver` (bundled with the dev requirements),
3. SQLite as a portable fallback.

Each test runs inside a transaction that is rolled back, so tests are isolated.
Override the server explicitly if you prefer a container:

```bash
TEST_DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/devpath_test pytest
```

### Frontend

```bash
cd frontend
npm test                 # Vitest + Testing Library
npm run test:coverage    # V8 coverage report
npm run typecheck
npm run build            # tsc -b + Vite production build
```

### End-to-end verification

This starts an isolated PostgreSQL cluster, applies the real Alembic migration, seeds
the roadmap, and exercises registration, progress, planner, projects, resources,
settings, persistence and cross-user isolation through the API:

```bash
cd backend
python -m scripts.e2e_check
```

---

## Environment variables

### Backend (`backend/.env`)

| Variable | Default | Purpose |
|---|---|---|
| `ENVIRONMENT` | `development` | App environment label |
| `DEBUG` | `true` | Debug mode |
| `APP_NAME` | `DevPath API` | OpenAPI title |
| `DATABASE_URL` | — | SQLAlchemy URL (`postgresql+psycopg://...`) |
| `DB_POOL_SIZE` / `DB_MAX_OVERFLOW` | `5` / `10` | Connection pool sizing |
| `SECRET_KEY` | — | HMAC key for access tokens — change in production |
| `JWT_ALGORITHM` | `HS256` | Access-token algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Access-token lifetime |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `14` | Refresh-token lifetime |
| `BCRYPT_ROUNDS` | `12` | Password hashing cost (tests use 4) |
| `CORS_ORIGINS` | `http://localhost:5173,...` | Comma-separated allowed origins |
| `SEED_ON_STARTUP` | `true` | Seed shared data (and demo user) on boot |
| `DEMO_USER_*` | demo values | Documented demo account |
| `LOG_LEVEL` / `LOG_FORMAT` | `INFO` / `json` | Logging configuration |

### Frontend

| Variable | Default | Purpose |
|---|---|---|
| `VITE_API_URL` | `/api/v1` | API base URL, inlined at build time |
| `VITE_PROXY_TARGET` | `http://localhost:8000` | Dev-server proxy target |

### Docker Compose (root `.env`)

`WEB_PORT`, `API_PORT`, `POSTGRES_PORT`, `POSTGRES_USER`, `POSTGRES_PASSWORD`,
`POSTGRES_DB`, `SECRET_KEY`, `ACCESS_TOKEN_EXPIRE_MINUTES`,
`REFRESH_TOKEN_EXPIRE_DAYS`, `BCRYPT_ROUNDS`, `ENVIRONMENT`, `DEBUG`,
`CORS_ORIGINS`, `SEED_ON_STARTUP`, `DEMO_USER_*`, `LOG_LEVEL`, `LOG_FORMAT` and
`VITE_API_URL`. See `.env.example`.

---

## Security notes

- Passwords are hashed with **bcrypt**; plaintext passwords are never stored or
  logged.
- Access tokens are short-lived JWTs. Refresh tokens are random opaque values;
  only their **SHA-256 digest** is persisted, and they are rotated on every refresh
  with revocation of the previous token.
- Every personal query is scoped by `user_id` from the verified token. Cross-user
  access returns `404` rather than leaking existence.
- Official seeded resources are read-only; only the owner can edit or delete custom
  resources.
- Request bodies cannot set ownership fields. Pydantic schemas reject malformed
  input with `422`.
- A wrong current password on `change-password` does **not** sign the user out.
- Responses include `X-Request-ID`; logs are structured in production (`LOG_FORMAT=json`).
- **Before deploying:** set a strong `SECRET_KEY`, a non-default database password,
  `DEBUG=false`, and an exact `CORS_ORIGINS` list. Serve over HTTPS.

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| `relation "..." does not exist` | Run `alembic upgrade head` before starting the API. |
| API cannot connect to PostgreSQL | Check `DATABASE_URL`; inside Compose the host is `db`, locally it is usually `localhost`. |
| Frontend gets 404s for `/api` | Start the backend on port 8000, or set `VITE_PROXY_TARGET`. |
| Tests skip PostgreSQL and use SQLite | Install dev requirements (`pip install -r requirements-dev.txt`) so `pgserver` is available, or set `TEST_DATABASE_URL`. |
| CORS errors | Add the exact frontend origin to `CORS_ORIGINS` (scheme, host and port must match). |
| Demo login fails | Run `python -m app.db.seed` with `SEED_ON_STARTUP=false`, or set `SEED_ON_STARTUP=true` and restart the API. |

---

## License

MIT. See the OpenAPI metadata for contact and license details.
