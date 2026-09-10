# TaskForge

TaskForge is a backend systems learning project following the canonical curriculum in `roadmap.md`.

## Current status

Day 5 / W1.5 is completed. The repository has a FastAPI API with in-memory CRUD plus a local PostgreSQL Compose setup, initial relational schema, seed data, and SQL validation scripts.

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

Apply schema and seed data inside the container:

```powershell
docker cp db taskforge-postgres-1:/tmp/taskforge/db
docker cp tests/sql taskforge-postgres-1:/tmp/taskforge/tests/sql
docker compose exec -T -w /tmp/taskforge postgres psql -U taskforge -d taskforge -f tests/sql/constraints.sql
docker compose exec -T -w /tmp/taskforge postgres psql -U taskforge -d taskforge -f tests/sql/queries.sql
```

The relational model is documented in `docs/relational-model.md`.

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

Data is in memory and disappears when the API process restarts.

Validation behavior:

- Unknown request fields are rejected.
- Path IDs must be valid UUIDs.
- Malformed IDs return `422`; valid missing resources return `404`.
- Task status cannot change directly from `todo` to `done`.
- Every response includes `X-Request-ID`; incoming `X-Request-ID` is preserved.
- Access logs are structured JSON and omit request bodies.

## Limitations

- No database, auth, tenant/workspace isolation, durable storage, or CI exists yet.




