# TaskForge Project Contract

## Day 1 scope

TaskForge starts as a local backend API. The first supported behavior is a live health endpoint that proves the API process can receive and answer an HTTP request.

## Supported endpoint

| Method | Path | Purpose | Success response |
| --- | --- | --- | --- |
| GET | `/health/live` | Confirms the API process is alive and request routing reaches application code. | `200 {"status":"ok"}` |

## Current non-goals

- No authentication or sessions yet.
- No workspace, project, or task data model yet.
- No database or persistence yet.
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
- Ruff format check: passed after formatting three Python files.
- Pytest: `1 passed`, with two dependency deprecation warnings from FastAPI/Starlette test client internals.

Runtime smoke check:

```powershell
python -m uvicorn taskforge.main:app --host 127.0.0.1 --port 8000
curl -i http://127.0.0.1:8000/health/live
```

Observed result: `StatusCode=200`, body `{"status":"ok"}`.
