# TaskForge

TaskForge is a backend systems learning project following the canonical curriculum in `roadmap.md`.

## Current status

Day 6 / W1.6 is in progress. The repository has a FastAPI API with PostgreSQL-backed runtime persistence by default, Alembic migration tooling, request-scoped database sessions, and isolated PostgreSQL integration tests. Memory storage remains available for focused unit-style tests.

## Records

- `roadmap.md`: canonical curriculum.
- `AGENTS.md`: tutoring and repository contract.
- `docs/tracker.md`: progress and resume point.
- `docs/learning.md`: learning notes.
- `docs/session-log.md`: session handoffs.
- `docs/decisions.md`: architecture decisions.
- `docs/design.md`: current architecture snapshot and daily design history.

## Setup and commands

Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
```

Optional local environment variables are shown in `.env.example`:

```powershell
TASKFORGE_ENVIRONMENT=local
TASKFORGE_LOG_LEVEL=INFO
TASKFORGE_STORAGE_BACKEND=postgres
TASKFORGE_DATABASE_URL=postgresql+psycopg://taskforge:taskforge_dev_password@127.0.0.1:5433/taskforge
```

Run the API:

```powershell
python -m uvicorn taskforge.main:app --reload
```

Smoke check:

```powershell
curl -i http://127.0.0.1:8000/health/live
```

Validate:

```powershell
python -m ruff check .
python -m ruff format --check .
python -m pytest -q
```

## Database

Start local PostgreSQL on host port `5433`:

```powershell
docker compose up -d postgres
```

For runtime development, apply Alembic migrations from the host:

```powershell
python -m alembic upgrade head
```

The Day 5 SQL lab scripts remain available for constraint/query practice. They copy SQL into the container and roll back their checks. The relational model is documented in `docs/relational-model.md`.

## API endpoints

- `GET /health/live`
- `POST /api/v1/projects`
- `GET /api/v1/projects?page_size=20`
- `GET /api/v1/projects/{project_id}`
- `PATCH /api/v1/projects/{project_id}`
- `DELETE /api/v1/projects/{project_id}`
- `POST /api/v1/projects/{project_id}/tasks`
- `GET /api/v1/projects/{project_id}/tasks?page_size=20`
- `GET /api/v1/projects/{project_id}/tasks/{task_id}`
- `PATCH /api/v1/projects/{project_id}/tasks/{task_id}`
- `DELETE /api/v1/projects/{project_id}/tasks/{task_id}`

With the default `postgres` backend, project/task data is durable in PostgreSQL and survives API process restarts. Tests that need fast in-memory behavior explicitly pass `storage_backend='memory'`.

Validation behavior:

- Unknown request fields are rejected.
- Path IDs must be valid UUIDs.
- Malformed IDs return `422`; valid missing resources return `404`.
- Task status cannot change directly from `todo` to `done`.
- Every response includes `X-Request-ID`; incoming `X-Request-ID` is preserved.
- Access logs are structured JSON and omit request bodies.

## Limitations

- No authentication, tenant/workspace authorization, readiness/dependency health, public deployment profile, or CI exists yet.




