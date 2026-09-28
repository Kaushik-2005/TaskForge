# TaskForge

TaskForge is a modular-monolith backend for workspaces, projects, tasks, and CSV exports.

The API uses FastAPI. PostgreSQL stores users, sessions, workspaces, memberships, projects, tasks, audit events, exports, jobs, and idempotency records. Redis stores derived project-summary cache entries and rate-limit counters. A separate worker processes export jobs.

## Components

- API: FastAPI and Uvicorn.
- Authentication: PostgreSQL-backed sessions, password hashing, HttpOnly cookies, and CSRF tokens.
- Authorization: workspace membership checks on workspace-scoped resources.
- Database: PostgreSQL, SQLAlchemy, psycopg, and Alembic.
- Cache and rate limits: Redis.
- Worker: bounded export worker with PostgreSQL claims, leases, retries, fencing tokens, and attempt-specific artifacts.
- Observability: request IDs, structured access logs, and bounded process-local HTTP metrics.
- Realtime lab: authenticated WebSocket subscriptions with bounded queues. The broker is process-local.
- Tests: pytest, HTTPX/FastAPI test client, PostgreSQL integration tests, and Ruff.
- Load testing: Locust workload and deterministic dataset seeder.

## Repository layout

```text
src/taskforge/       application code
migrations/          Alembic migrations
tests/               unit, API, and PostgreSQL integration tests
load_tests/          Locust workload and load-test instructions
scripts/             local data seeding scripts
design.md            HLD and LLD
roadmap.md           learning roadmap
```

## Requirements

- Python 3.12
- Docker Desktop
- PostgreSQL 17 for the local Compose service
- Redis 7 for the local Compose service

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
```

Start dependencies:

```powershell
docker compose up -d postgres redis
```

Apply migrations:

```powershell
python -m alembic upgrade head
```

## Run the API and worker

Terminal 1:

```powershell
python -m uvicorn taskforge.main:app --reload
```

Terminal 2:

```powershell
python -m taskforge.worker
```

Health check:

```powershell
curl.exe http://127.0.0.1:8000/health/live
```

Expected response:

```json
{"status":"ok"}
```

## API surface

Authentication:

- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/logout`
- `GET /api/v1/auth/me`

Workspace resources:

- `POST /api/v1/workspaces`
- `GET /api/v1/workspaces/{workspace_id}/memberships`
- `POST /api/v1/workspaces/{workspace_id}/memberships`
- `GET|POST /api/v1/workspaces/{workspace_id}/projects`
- `GET|POST /api/v1/workspaces/{workspace_id}/projects/{project_id}/tasks`
- `GET|PATCH|DELETE /api/v1/workspaces/{workspace_id}/projects/{project_id}/tasks/{task_id}`

Exports:

- `POST /api/v1/workspaces/{workspace_id}/exports`
- `GET /api/v1/exports/{export_id}`
- `GET /api/v1/exports/{export_id}/download`

`POST /exports` creates the export, job, and idempotency record in one transaction. It returns `202 Accepted` only after the transaction commits. Reusing an idempotency key with a different request returns `409 Conflict`.

## Data and consistency rules

- PostgreSQL is the source of truth.
- Workspace membership controls access.
- Authorization is applied before protected cache or file-path access.
- Task updates require `expected_version` and return `409` for stale versions.
- Task lists use bounded page sizes and deterministic cursor ordering.
- Export acceptance commits the export and pending job together.
- Workers claim jobs with row locking and commit ownership before slow work.
- Lease expiry permits recovery; it does not prove the old worker stopped.
- Completion requires the current ownership token.
- Retries are bounded and use attempt-specific output paths.
- Redis is disposable. Important state is not stored only in Redis.

## Load testing

Seed the fixed local dataset:

```powershell
python -m scripts.seed_load_data
. .\.dist\load-test.env.ps1
```

The default dataset contains 100 users, 20 workspaces, 400 projects, and 40,000 tasks.

Run the baseline:

```powershell
python -m locust -f load_tests/locustfile.py --headless --host http://127.0.0.1:8000 --users 50 --spawn-rate 0.5 --run-time 12m --csv results/taskforge-pool20
```

Workload weights are 70% task reads, 20% task writes, and 10% export workflows. Export workflows perform an export request and a status request.

### Measured results

Final local run:

- Python 3.12.0, PostgreSQL 17.11, Redis 7.4.11
- 50 users, worker concurrency 2
- Database pool: 20 connections, 10 overflow
- 17,933 requests
- 6 failures: 0.03%
- 24.94 requests/second
- p50: 37 ms
- p95: 77 ms
- p99: 130 ms
- p99.9: 1,200 ms
- Maximum: 1,600 ms

These are local measurements, not production capacity claims.

## Validation

```powershell
python -m ruff check .
python -m ruff format --check .
python -m pytest -q
```

The final validation run passed all three commands.

