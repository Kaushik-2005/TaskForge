# Session Log

## 2026-09-09 - Day 1 / W1.1 - Roadmap startup
- Starting point: Repository contained AGENTS.md and roadmap.md only.
- Concepts and work covered: First-run inspection and learning-record initialization.
- Learner evidence: Pending; guided learning has not yet checked understanding.
- Files changed: docs/tracker.md, docs/learning.md, docs/session-log.md, docs/decisions.md, docs/design.md, README.md.
- Commands run and outcomes: `Get-ChildItem -Force` listed AGENTS.md and roadmap.md; `git status --short` failed because the folder is not a Git repository; `Get-ChildItem -Force docs` failed because docs/ was absent.
- Problems and resolutions: Missing docs/ records were initialized. Git tracking remains unavailable until a repository is initialized or connected.
- Weak areas / incomplete work: All Day 1 understanding, exercise, build, and validation evidence remain incomplete.
- Exact next action: Teach the first Day 1 concept: the HTTP request journey and where failures happen.
- Current repository state / relevant uncommitted work: Git status unavailable; folder is not a Git repository.

## 2026-09-09 - Day 1 / W1.1 - Health endpoint scaffold
- Starting point: Day 1 records existed; no runtime API implementation existed.
- Concepts and work covered: Request journey, 404 versus connection failure, HTTP statelessness versus application sessions, and health endpoint scope.
- Learner evidence: Learner correctly explained route-level 404 evidence, stateless HTTP with cookies/tokens carrying identity proof, and the successful curl path through address/port, TCP, GET path, route/handler, and 200 response.
- Files changed: `.gitignore`, `.env.example`, `pyproject.toml`, `README.md`, `src/taskforge/__init__.py`, `src/taskforge/config.py`, `src/taskforge/main.py`, `tests/test_health.py`, `docs/project-contract.md`, `docs/tracker.md`, `docs/learning.md`, `docs/design.md`, `docs/session-log.md`.
- Commands run and outcomes: Python 3.12.0 detected; virtual environment created; dependencies installed with `.\.venv\Scripts\python.exe -m pip install -e ".[dev]"`; ruff check passed; ruff format check passed after formatting; pytest passed with `1 passed` and two dependency deprecation warnings; live Uvicorn smoke check returned `StatusCode=200` and body `{"status":"ok"}`.
- Problems and resolutions: Normal patch/sandboxed command execution intermittently failed because `codex-windows-sandbox-setup.exe` was unavailable; local workspace edits and validation were completed with explicit escalation.
- Weak areas / incomplete work: Continue reinforcing that health checks prove a narrow request path only.
- Exact next action: Start Day 2 / W1.2 by designing resource routes and status/error contracts for in-memory project/task CRUD.
- Current repository state / relevant uncommitted work: Git status unavailable because this folder is not currently a Git repository.

## 2026-09-09 - Day 2 / W1.2 - In-memory project/task contracts
- Starting point: Day 1 completed with health endpoint and no resource API.
- Concepts and work covered: Resource-style routes, GET safety, POST creation, `201 Created`, `Location` header, DELETE idempotency, nested task routes, page-size bounds, and error envelopes.
- Learner evidence: Learner chose `POST /api/v1/projects` over action-style GET, identified `201 Created`, explained DELETE idempotency as final-state semantics, and completed the endpoint table with minor route-shape corrections.
- Files changed: `README.md`, `docs/project-contract.md`, `docs/tracker.md`, `docs/learning.md`, `docs/design.md`, `docs/session-log.md`, `src/taskforge/api.py`, `src/taskforge/main.py`, `src/taskforge/models.py`, `src/taskforge/store.py`, `tests/test_projects_tasks.py`.
- Commands run and outcomes: Ruff check passed; ruff format check passed; pytest passed with `8 passed` and two dependency deprecation warnings. An earlier pytest run had one failing wrong-method error-envelope test; fixed by handling `StarletteHTTPException`.
- Problems and resolutions: Corrected singular `/task/{task_id}` table route to plural `/tasks/{task_id}`; made nested task item routes report missing parent projects explicitly.
- Weak areas / incomplete work: Need Day 3 validation depth for unknown fields, null versus missing, and stricter response boundaries.
- Exact next action: Start Day 3 / W1.3 by classifying malformed JSON, invalid IDs, oversized fields, forbidden state changes, and unexpected fields by rejection layer.
- Current repository state / relevant uncommitted work: Git is now initialized; README had a prior uncommitted change removing the stale non-Git limitation and was preserved.

## 2026-09-09 - Day 3 / W1.3 - Serialization and validation boundaries
- Starting point: Day 2 completed with in-memory CRUD, but models still allowed unknown fields and string-shaped IDs.
- Concepts and work covered: JSON parsing versus schema validation, contract validation, domain validation, missing versus null, UUID path parsing, response field boundaries, and task status transitions.
- Learner evidence: Learner correctly classified malformed JSON, empty name, unexpected `is_admin`, and forbidden task transition by rejection layer.
- Files changed: `README.md`, `docs/project-contract.md`, `docs/tracker.md`, `docs/learning.md`, `docs/design.md`, `docs/session-log.md`, `src/taskforge/api.py`, `src/taskforge/models.py`, `src/taskforge/store.py`, `tests/test_projects_tasks.py`, `tests/test_validation.py`.
- Commands run and outcomes: Initial Day 3 validation tests failed as expected for missing behavior; final ruff check passed, format check passed, and pytest passed with `17 passed` and two dependency deprecation warnings.
- Problems and resolutions: Tightening path IDs from strings to UUIDs changed malformed `missing` IDs from `404` to `422`; regression tests were corrected to use valid absent UUIDs when testing missing resources.
- Weak areas / incomplete work: Global payload byte-size limits and service-layer ownership are deferred to later modules.
- Exact next action: Start Day 4 / W1.4 by tracing a task update through handler, service, repository/store, and error mapping boundaries.
- Current repository state / relevant uncommitted work: Day 3 files modified; run `git status --short` for current diff before committing.

## 2026-09-09 - Day 3 / W1.3 - Null handling follow-up
- Starting point: Day 3 validation was passing with 17 tests, but explicit `null` task title plus another change was not separately covered.
- Concepts and work covered: Missing versus explicit null in PATCH and JSON-safe validation error detail serialization.
- Learner evidence: Same Day 3 classification evidence applies.
- Files changed: `src/taskforge/models.py`, `src/taskforge/main.py`, `tests/test_validation.py`, `docs/tracker.md`, `docs/learning.md`, `docs/design.md`, `docs/project-contract.md`, `docs/session-log.md`.
- Commands run and outcomes: Ruff check passed; ruff format check passed; pytest passed with `18 passed` and two dependency deprecation warnings.
- Problems and resolutions: Pydantic validation details included a raw `ValueError`; fixed by encoding `exc.errors()` with FastAPI `jsonable_encoder` before returning JSON.
- Weak areas / incomplete work: Global request body byte-size limits remain deferred.
- Exact next action: Start Day 4 / W1.4 with layer separation.
- Current repository state / relevant uncommitted work: Day 3 files modified; run `git status --short` before committing.

## 2026-09-09 - Day 4 / W1.4 - Layers, config, and request context
- Starting point: Day 3 completed with route handlers calling the in-memory store directly and the status transition rule living near storage.
- Concepts and work covered: Route/service/store separation, exception-handler ownership, middleware responsibilities, request IDs, structured logs, and startup settings validation.
- Learner evidence: Learner correctly placed the task transition rule in the service layer, corrected validation error-envelope ownership to exception handlers, and traced a forbidden task update through route, service, store, error mapping, and `409 Conflict` response.
- Files changed: `.env.example`, `README.md`, `docs/decisions.md`, `docs/project-contract.md`, `docs/tracker.md`, `docs/learning.md`, `docs/design.md`, `docs/session-log.md`, `src/taskforge/api.py`, `src/taskforge/config.py`, `src/taskforge/errors.py`, `src/taskforge/main.py`, `src/taskforge/services.py`, `src/taskforge/store.py`, `tests/test_app_boundaries.py`, `tests/test_services.py`.
- Commands run and outcomes: Ruff check passed; ruff format check passed; pytest passed with `25 passed` and two dependency deprecation warnings. Ruff fixed one import-order issue.
- Problems and resolutions: Moved business transition logic out of `InMemoryStore`; added ADR-001 to record the boundary decision.
- Weak areas / incomplete work: Live log inspection, database repository boundaries, and global payload byte-size limits remain future work.
- Exact next action: Start Day 5 / W1.5 by drawing the relational model and explaining why database constraints backstop API validation.
- Current repository state / relevant uncommitted work: Day 4 files modified; run `git status --short` before committing.

## 2026-09-10 - Day 5 / W1.5 - Relational model and PostgreSQL constraint lab
- Starting point: Day 4 completed with in-memory API, service layer, request IDs, structured logs, and startup config validation.
- Concepts and work covered: Relational entities, primary keys, foreign keys, unique constraints, check constraints, authorized joins, aggregate counts, and why database constraints backstop API validation.
- Learner evidence: Learner explained referential integrity, membership uniqueness, proposed a users/workspaces/memberships/projects/tasks ER model, and wrote authorized task and project-count SQL queries with minor syntax correction.
- Files changed: `README.md`, `compose.yaml`, `db/schema.sql`, `db/seed.sql`, `docs/decisions.md`, `docs/project-contract.md`, `docs/relational-model.md`, `docs/tracker.md`, `docs/learning.md`, `docs/design.md`, `docs/session-log.md`, `tests/sql/constraints.sql`, `tests/sql/queries.sql`.
- Commands run and outcomes: Docker and Compose detected. Initial Compose startup timed out; retry showed port `5432` was already allocated. Changed host port to `5433`; PostgreSQL started and became healthy. SQL constraint script passed. SQL query script passed. Ruff check passed, format check passed, pytest passed with `25 passed` and two dependency deprecation warnings.
- Problems and resolutions: Port conflict on `5432` resolved by mapping local PostgreSQL to host `5433`. SQL query script initially used a nonexistent `fail()` helper; replaced with PL/pgSQL assertions.
- Weak areas / incomplete work: API still uses in-memory storage. Migration tooling, request-scoped DB sessions, rollback behavior, connection pools, and integration test isolation are Day 6 work.
- Exact next action: Start Day 6 / W1.6 by explaining request-scoped DB sessions, commit/rollback, and connection pool ownership.
- Current repository state / relevant uncommitted work: Day 5 files modified; PostgreSQL container may still be running on host port `5433`.
