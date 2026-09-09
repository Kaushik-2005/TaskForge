# TaskForge Project Contract

## Day 2 scope

TaskForge is a local backend API with a live health endpoint and in-memory project/task CRUD. The Day 2 API is intentionally not durable; persistence starts later in Week 1.

## Supported endpoints

| Method | Path | Purpose | Success response |
| --- | --- | --- | --- |
| GET | `/health/live` | Confirms the API process is alive and request routing reaches application code. | `200 {"status":"ok"}` |
| POST | `/api/v1/projects` | Create a project. | `201 ProjectRead`, with `Location` header |
| GET | `/api/v1/projects?page_size=20` | List projects in creation order. | `200 list[ProjectRead]` |
| GET | `/api/v1/projects/{project_id}` | Read one project. | `200 ProjectRead` |
| PATCH | `/api/v1/projects/{project_id}` | Partially update a project's name. | `200 ProjectRead` |
| DELETE | `/api/v1/projects/{project_id}` | Delete one project and its in-memory tasks. | `204 No Content` |
| POST | `/api/v1/projects/{project_id}/tasks` | Create a task under a project. | `201 TaskRead`, with `Location` header |
| GET | `/api/v1/projects/{project_id}/tasks?page_size=20` | List tasks for a project in creation order. | `200 list[TaskRead]` |
| GET | `/api/v1/projects/{project_id}/tasks/{task_id}` | Read one task under a project. | `200 TaskRead` |
| PATCH | `/api/v1/projects/{project_id}/tasks/{task_id}` | Partially update task title and/or status. | `200 TaskRead` |
| DELETE | `/api/v1/projects/{project_id}/tasks/{task_id}` | Delete one task. | `204 No Content` |

## Error contract

Expected HTTP and validation errors use this envelope:

```json
{
  "error": {
    "code": "not_found",
    "message": "Project not found"
  }
}
```

Validation errors use `422` and `code: validation_error`. Page size is bounded from 1 through 100.

## Current non-goals

- No authentication or sessions yet.
- No database or persistence yet; all project/task data is process-local memory.
- No tenant/workspace authorization yet.
- No readiness/dependency health yet.
- No public deployment profile yet.

## Environment

- Python 3.12.0 was detected locally.
- The chosen stack is Python, FastAPI, pytest, and ruff.
- Local development uses plain HTTP on `127.0.0.1`. TLS and production proxy behavior are future topics.

## Validation evidence

Executed on 2026-09-09:

```powershell
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m ruff format --check .
.\.venv\Scripts\python.exe -m pytest -q
```

Results:

- Ruff lint: passed.
- Ruff format check: passed.
- Pytest: `8 passed`, with two dependency deprecation warnings from FastAPI/Starlette test client internals.

Day 1 runtime smoke check observed: `StatusCode=200`, body `{"status":"ok"}`.
