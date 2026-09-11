# TaskForge Project Contract

## Current scope

TaskForge is a local backend API with a live health endpoint, project/task CRUD, stricter serialization/validation boundaries, service-layer business rules, request IDs, structured access logs, startup settings validation, PostgreSQL-backed runtime persistence by default, optional project-name filtering, and authentication with server-side sessions. Memory storage remains available only for focused tests.

## Supported endpoints

| Method | Path | Purpose | Success response |
| --- | --- | --- | --- |
| GET | `/health/live` | Confirms the API process is alive and request routing reaches application code. | `200 {"status":"ok"}` |
| POST | `/api/v1/auth/register` | Create a user with email/password. | `201 UserRead` |
| POST | `/api/v1/auth/login` | Verify credentials, create a server-side session, set the session cookie, and return a CSRF token. | `200 AuthSessionRead` |
| POST | `/api/v1/auth/logout` | Revoke the current session and clear the cookie. Requires CSRF when a session cookie is present. | `204 No Content` |
| GET | `/api/v1/auth/me` | Read the current authenticated user from a valid session cookie. | `200 UserRead` |
| POST | `/api/v1/projects` | Create a project. | `201 ProjectRead`, with `Location` header |
| GET | `/api/v1/projects?page_size=20&name_contains=plan` | List projects in creation order, optionally filtered by case-insensitive name substring. | `200 list[ProjectRead]` |
| GET | `/api/v1/projects/{project_id}` | Read one project. | `200 ProjectRead` |
| PATCH | `/api/v1/projects/{project_id}` | Partially update a project's name. | `200 ProjectRead` |
| DELETE | `/api/v1/projects/{project_id}` | Delete one project and its tasks. | `204 No Content` |
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

Validation errors use `422` and `code: validation_error`. Auth failures use `401 invalid_credentials` or `401 unauthenticated`; duplicate registration uses `409 email_already_registered`; missing/invalid CSRF uses `403 csrf_required`. Page size is bounded from 1 through 100. `name_contains` is optional, case-insensitive, and must not be empty when supplied. Unknown request fields are rejected. Path IDs must be valid UUIDs. Valid UUIDs that do not exist return `404`; malformed IDs return `422`. Task status cannot change directly from `todo` to `done`; that domain violation returns `409 invalid_state_transition`.

## Current non-goals

- No authentication-backed user/workspace isolation yet; project/task routes still write into a configured default workspace until Day 9 authorization work.
- No tenant/workspace authorization yet.
- No readiness/dependency health yet.
- No public deployment profile yet.

## Environment

- Python 3.12.0 was detected locally.
- The chosen stack is Python, FastAPI, pytest, and ruff.
- Local development uses plain HTTP on `127.0.0.1`, so `TASKFORGE_SESSION_COOKIE_SECURE=false` is the local exception. Production HTTPS should use `TASKFORGE_SESSION_COOKIE_SECURE=true` so the browser only sends the session cookie over HTTPS.

## Validation evidence

Latest core validation executed on 2026-09-11:

```powershell
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m ruff format --check .
.\.venv\Scripts\python.exe -m pytest -q
```

Results:

- Ruff lint: passed.
- Ruff format check: passed.
- Pytest: `48 passed`, with two dependency deprecation warnings from FastAPI/Starlette test client internals. PostgreSQL integration tests create/drop isolated temporary databases and run Alembic migrations.

Day 1 runtime smoke check observed: `StatusCode=200`, body `{"status":"ok"}`.



## Runtime boundary behavior

- Route handlers own HTTP status codes, response headers, and mapping service errors to HTTP errors.
- `TaskForgeService` owns business rules such as task status transitions.
- `PostgresStore` owns runtime SQL data access. `InMemoryStore` remains available for focused tests only.
- Every response includes `X-Request-ID`; a supplied request ID is preserved.
- Access logs are JSON records with request ID, method, path, status code, and duration. Request bodies are not logged.
- Invalid startup settings, such as an unsupported environment, prevent app construction.

## Database contract

Day 6 introduces Alembic migrations and SQLAlchemy/psycopg runtime persistence. Day 5 SQL files remain as relational modeling lab material.

Current SQL guarantees tested:

- Projects cannot reference a missing workspace.
- Memberships cannot duplicate `(user_id, workspace_id)`.
- Tasks cannot use a status outside `todo`, `in_progress`, `done`.
- Authorized task lookup joins memberships, projects, and tasks.
- Project task counts include projects with zero tasks.

The default runtime backend uses PostgreSQL through request-scoped SQLAlchemy sessions. Repository methods flush changes but do not commit. The request dependency commits once after a successful handler or rolls back on exception.

## Authentication contract

- Passwords are stored with a maintained password hashing library, not plaintext or reversible encryption.
- Raw session and CSRF tokens are generated with high-entropy randomness; only token hashes are stored in PostgreSQL.
- `taskforge_session` is HttpOnly, SameSite=Lax, path `/`, and configurable Secure.
- `/api/v1/auth/me` returns `401 unauthenticated` for missing, expired, or revoked sessions.
- Cookie-authenticated unsafe project/task mutations require `X-CSRF-Token`.


