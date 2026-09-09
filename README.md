# TaskForge

TaskForge is a backend systems learning project following the canonical curriculum in `roadmap.md`.

## Current status

Day 2 / W1.2 is completed. The repository has a minimal FastAPI API with a live health endpoint and in-memory project/task CRUD under `/api/v1`.

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

## Limitations

- No database, auth, tenant/workspace isolation, durable storage, or CI exists yet.

