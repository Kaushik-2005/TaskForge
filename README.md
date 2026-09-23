# TaskForge

TaskForge is a backend systems learning project following the canonical curriculum in `roadmap.md`.

## Current status

Day 17 / W3.3 idempotency and reliable retries is complete. The repository has a FastAPI API with PostgreSQL-backed runtime persistence by default, Alembic migration tooling, request-scoped database sessions, isolated PostgreSQL integration tests, authentication, workspace authorization, project/task CRUD, version-checked task updates, task update audit events, deterministic task cursor pagination, a measured task-list index, Redis cache/rate-limit support, and durable export jobs with atomic claims, leases, ownership tokens, idempotency keys, bounded retries, checksummed attempt-specific artifacts, and bounded worker concurrency. Memory storage remains available for focused unit-style tests.

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

Run one worker pass, or keep polling for pending exports:

```powershell
python -m taskforge.worker --once
python -m taskforge.worker
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

Authentication:

- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/logout`
- `GET /api/v1/auth/me`

Project and task API:

- `GET /health/live`
- `POST /api/v1/projects`
- `GET /api/v1/projects?page_size=20&name_contains=plan`
- `GET /api/v1/projects/{project_id}`
- `PATCH /api/v1/projects/{project_id}`
- `DELETE /api/v1/projects/{project_id}`
- `POST /api/v1/projects/{project_id}/tasks`
- `GET /api/v1/projects/{project_id}/tasks?page_size=20&after_created_at=...&after_id=...`
- `GET /api/v1/projects/{project_id}/tasks/{task_id}`
- `PATCH /api/v1/projects/{project_id}/tasks/{task_id}` requires `expected_version`
- `DELETE /api/v1/projects/{project_id}/tasks/{task_id}`

Workspace and export API:

- `POST /api/v1/workspaces/{workspace_id}/exports` returns `202 Accepted` after the export and pending job commit together.
- `GET /api/v1/exports/{export_id}` returns the authorized export status.

With the default `postgres` backend, user/session/project/task data is durable in PostgreSQL and survives API process restarts. Tests that need fast in-memory behavior explicitly pass `storage_backend='memory'`.

Validation behavior:

- Unknown request fields are rejected.
- Path IDs must be valid UUIDs. `name_contains` filters projects case-insensitively and rejects an empty value.
- Malformed IDs return `422`; valid missing resources return `404`.
- Task status cannot change directly from `todo` to `done`.
- Task PATCH requests require `expected_version`; stale versions return `409 stale_task_version` instead of silently overwriting newer data.
- Task list cursor parameters `after_created_at` and `after_id` must be supplied together. Task lists order by `(created_at, id)` for deterministic pagination.
- Every response includes `X-Request-ID`; incoming `X-Request-ID` is preserved.
- Login sets an HttpOnly `taskforge_session` cookie and returns a CSRF token in the response body.
- Unsafe project/task mutations with a session cookie require `X-CSRF-Token`.
- Local HTTP uses `TASKFORGE_SESSION_COOKIE_SECURE=false`; production HTTPS should set it to `true`.
- Access logs are structured JSON and omit request bodies.
- Export status is tenant-scoped. A completed export reports a private output reference; serving/download authorization is deferred.

## Limitations

- Workspace-scoped project/task/export authorization is implemented. Legacy unauthenticated project/task routes still exist for local compatibility and need reconciliation with the workspace-scoped route surface.
- Day 17 uses user/workspace/operation-scoped idempotency, bounded retry attempts, temporary-file cleanup, attempt-specific output paths, and SHA-256 artifact metadata. Live process recovery testing, secure file download, and broker/outbox publication remain future work.
- No readiness/dependency health, cache, public deployment profile, or CI exists yet.






