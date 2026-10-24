# DevPath — Implementation Plan

Personal learning roadmap & progress tracker for becoming a Backend + DevOps Engineer
(Java / Spring Boot). React + Vite + TS frontend, Python + FastAPI backend, PostgreSQL.

## 1. Architecture

```
┌──────────────────────────────┐        /api/v1/*  (JWT Bearer)
│  frontend/  React 19 + Vite   │ ───────────────────────────────┐
│  Tailwind v4 · Lucide · Recharts│                                │
│  TanStack Query · React Router │ ◀─── JSON (uniform error shape) │
└──────────────────────────────┘                                 │
                                                                ▼
                                            ┌────────────────────────────────┐
                                            │ backend/  FastAPI             │
                                            │  routers → services → repos    │
                                            │  SQLAlchemy 2.0 (sync)        │
                                            │  Alembic migrations            │
                                            └───────────────┬────────────────┘
                                                            │
                                                 ┌──────────▼──────────┐
                                                 │  PostgreSQL 16     │
                                                 │  docker compose    │
                                                 └─────────────────────┘
```

Layer rules
- **routers** (`app/api/v1/*`) — HTTP only: parse/validate input via Pydantic schemas,
  resolve the *current* user from the JWT (never from the request body), call a service,
  return a response schema.
- **services** (`app/services/*`) — all business rules, transactions, progress maths.
- **repositories** (`app/repositories/*`) — all SQL, no business logic.
- **models** (`app/models/*`) — SQLAlchemy 2.0 ORM tables.
- **schemas** (`app/schemas/*`) — Pydantic v2 request/response contracts (OpenAPI source).

## 2. Data model (PostgreSQL)

| Table | Scope | Notes |
|---|---|---|
| `users` | global | unique email + username, bcrypt hash, role |
| `refresh_tokens` | global | SHA-256 hashed token, revoked_at |
| `roadmap_phases` | global seed | 7 phases, `order_index`, `month_label`, `duration_months` |
| `topics` | global seed | FK→phase, `subtopics` JSON, `estimated_minutes` |
| `topic_resources` | global seed | join topics↔resources |
| `resources` | global seed | 13 categories, official docs URLs |
| `topic_progress` | **per user** | status, priority, started_at, completed_at, rating, version |
| `topic_notes` | **per user** | FK user+topic |
| `topic_checklist_items` | **per user** | FK user+topic, done flag |
| `daily_tasks` | **per user** | date, category, priority, est/actual minutes, note, carried_from |
| `study_sessions` | **per user** | minutes — the ONLY source of truth for study hours |
| `projects` | **per user** | seeded per user from templates |
| `project_milestones` | **per user** | completion % = done/total |
| `project_checklist_items` | **per user** | |
| `user_resource_links` | **per user** | bookmarked flag, linked_topic_id |
| `user_preferences` | **per user** | daily goal, roadmap start, theme, reminders, phase overrides |

Integrity: FKs with `ON DELETE CASCADE`, indexes on every FK + on
`(user_id, topic_id)`, `(user_id, task_date)`, `(user_id, session_date)`,
unique constraints on `(user_id, topic_id)`, `(user_id, task_date, title)`,
`users.email`, `users.username`.

## 3. Progress rules (all derived from persisted rows — no hardcoded numbers)

- Topic completion = `status == 'completed'` / total topics.
- Phase completion = completed topics in phase / total topics in phase.
- Overall = completed topics / all roadmap topics.
- Project completion = completed milestones / total milestones.
- Study hours = `SUM(study_sessions.minutes) / 60`.
- **Streak** = consecutive *study days* (a day with ≥1 study session or a completed
  task with actual_minutes > 0), counting back from today (or yesterday).
- Re-opening a topic clears `completed_at`; re-completing sets it once. Because progress
  is derived from the current status (never accumulated counters) a topic can never be
  counted twice.

## 4. Build order

1. `backend/` — config, db, models, Alembic, security, auth, seed, health.
2. Roadmap API + dashboard API + progress maths.
3. Planner API (tasks / sessions / calendar / streak).
4. Projects + resources APIs.
5. Settings, export (JSON/CSV), import with validation, reset.
6. `frontend/` — auth flow, app shell (sidebar + mobile nav), 6 pages, components.
7. Tests: Pytest (auth, ownership, progress, planner, projects, resources, settings)
   and Vitest + RTL (api client, format utils, progress maths, components).
8. Docker Compose, `.env.example`, `.gitignore`, README, demo account script.

## 5. Directory structure

```
skill-tracker/
├── README.md · IMPLEMENTATION_PLAN.md · docker-compose.yml · .env.example · .gitignore
├── backend/
│   ├── app/{core,db,models,schemas,api/v1,services,repositories,tests}
│   ├── alembic/versions
│   └── pyproject.toml · Dockerfile · .env.example
└── frontend/
    ├── src/{api,components,hooks,pages,lib,types,context}
    └── package.json · vite.config.ts · Dockerfile · nginx.conf
```
