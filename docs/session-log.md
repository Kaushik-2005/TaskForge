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

## 2026-09-10 - Day 6 / W1.6 - PostgreSQL persistence implementation
- Starting point: Day 5 completed with PostgreSQL schema/query labs, but runtime API still used in-memory storage.
- Concepts and work covered: Request-scoped sessions, commit/rollback ownership, repository flush without commit, migration ownership, isolated test databases, and PostgreSQL repository boundaries.
- Learner evidence: Learner correctly explained atomic rollback for a multi-step operation and distinguished `flush()` from `commit()`.
- Files changed: `.env.example`, `README.md`, `alembic.ini`, `migrations/`, `pyproject.toml`, `src/taskforge/api.py`, `src/taskforge/config.py`, `src/taskforge/db.py`, `src/taskforge/db_models.py`, `src/taskforge/main.py`, `src/taskforge/repositories.py`, `src/taskforge/services.py`, tests, and Day 6 docs.
- Commands run and outcomes: Installed new dependencies with `.\.venv\Scripts\python.exe -m pip install -e ".[dev]"`. `.\.venv\Scripts\python.exe -m ruff check .` passed. `.\.venv\Scripts\python.exe -m ruff format --check .` passed. `.\.venv\Scripts\python.exe -m pytest -q` passed with `28 passed` and two dependency warnings.
- Problems and resolutions: Normal patch tool remained unavailable because the Windows sandbox helper was missing; scoped PowerShell writes were used. FastAPI `on_event` shutdown warning was removed by switching to lifespan disposal. Alembic path separator warning was removed with `path_separator = os`.
- Weak areas / incomplete work: Learner still needs to explain total database connection demand across multiple API processes before Day 6 is complete.
- Exact next action: Ask the pool-demand question, then mark Day 6 complete if answered correctly and prepare Day 7 foundation review.
- Current repository state / relevant uncommitted work: Day 6 persistence files and docs are modified/uncommitted; PostgreSQL container may still be running on host port `5433`.

## 2026-09-10 - Day 6 / W1.6 - Completion check
- Starting point: Day 6 implementation was validated; pool-demand understanding check remained open.
- Concepts and work covered: Total PostgreSQL connection demand across multiple API worker processes.
- Learner evidence: Learner correctly calculated `(pool_size + max_overflow) * worker_processes`; for 4 workers with pool size 5 and overflow 2, maximum demand is 28 connections because each worker process owns its own pool.
- Files changed: `docs/tracker.md`, `docs/learning.md`, `docs/design.md`, `docs/session-log.md`.
- Commands run and outcomes: No validation commands needed; documentation-only completion update.
- Problems and resolutions: None.
- Weak areas / incomplete work: Existing developer database migration state may need cleanup/stamping before using it as an Alembic-managed database.
- Exact next action: Start Day 7 / W1.7 foundation review when requested.
- Current repository state / relevant uncommitted work: Day 6 implementation and documentation changes remain uncommitted.

## 2026-09-10 - Day 6 / W1.6 - Alembic URL precedence fix
- Starting point: Manual `python -m alembic upgrade head` with `TASKFORGE_DATABASE_URL` set still attempted to use the `alembic.ini` URL, causing `DuplicateTable` against an existing schema.
- Concepts and work covered: Migration configuration precedence and why manual tests must target the intended database.
- Learner evidence: Learner surfaced the actual migration traceback from manual testing.
- Files changed: `migrations/env.py`, `docs/session-log.md`.
- Commands run and outcomes: `.\.venv\Scripts\python.exe -m ruff check .` passed. `.\.venv\Scripts\python.exe -m ruff format --check .` passed. `.\.venv\Scripts\python.exe -m pytest -q tests\test_postgres_persistence.py` passed with `3 passed` and two dependency warnings.
- Problems and resolutions: Fixed `migrations/env.py` so `TASKFORGE_DATABASE_URL` takes precedence over the default URL in `alembic.ini`.
- Weak areas / incomplete work: Be explicit about which database a migration command targets.
- Exact next action: Recreate or choose a clean manual database, set `TASKFORGE_DATABASE_URL`, and rerun `python -m alembic upgrade head`.
- Current repository state / relevant uncommitted work: Day 6 implementation plus Alembic URL precedence fix remain uncommitted.

## 2026-09-10 - Day 6 / W1.6 - Manual persistence verification
- Starting point: PostgreSQL persistence implementation and Alembic URL precedence fix were complete; manual API persistence needed confirmation.
- Concepts and work covered: Runtime persistence across API process restart.
- Learner evidence: Learner created a project through the API, stopped Uvicorn, restarted Uvicorn, and confirmed the project still appeared in `GET /api/v1/projects`.
- Files changed: `docs/tracker.md`, `docs/design.md`, `docs/session-log.md`.
- Commands run and outcomes: Manual curl commands run by learner; create/list worked after correcting PowerShell JSON quoting; list still worked after Uvicorn restart.
- Problems and resolutions: PowerShell curl JSON quoting initially produced `422 json_invalid`; resolved by using single quotes around JSON without backslashes.
- Weak areas / incomplete work: None for Day 6 manual persistence.
- Exact next action: Commit Day 6 changes or start Day 7 / W1.7 foundation review when requested.
- Current repository state / relevant uncommitted work: Day 6 implementation and documentation changes remain uncommitted.

## 2026-09-11 - Day 7 / W1.7 - Foundation review and filter task
- Starting point: Day 6 completed; Day 7 Week 1 review started on September 11, 2026.
- Concepts and work covered: Week 1 conceptual review, SQL aggregate debugging, and a small filtered project-list endpoint.
- Learner evidence: Learner correctly answered five review questions, debugged `COUNT(*)` with `LEFT JOIN`, and implemented `name_contains` filtering across route, service, memory store, PostgreSQL repository, and tests.
- Files changed: `src/taskforge/api.py`, `src/taskforge/services.py`, `src/taskforge/store.py`, `src/taskforge/repositories.py`, `tests/test_projects_tasks.py`, `tests/test_postgres_persistence.py`, `docs/tracker.md`, `docs/learning.md`, `docs/design.md`, `docs/session-log.md`.
- Commands run and outcomes: `.\.venv\Scripts\python.exe -m ruff check .` passed. `.\.venv\Scripts\python.exe -m ruff format --check .` passed. `.\.venv\Scripts\python.exe -m pytest -q` passed with `34 passed` and two dependency warnings.
- Problems and resolutions: Initial code passed behavior tests but needed formatting; protocol signature also needed to match the new filter argument. Both were corrected.
- Weak areas / incomplete work: Day 7 final milestone review still needs fresh-start setup evidence and design/contract reconciliation.
- Exact next action: Review README/setup from a fresh-start perspective, reconcile docs/design.md and project contract, then decide whether Week 1 gate can be marked complete.
- Current repository state / relevant uncommitted work: Day 6 and Day 7 implementation/documentation changes remain uncommitted.

## 2026-09-11 - Day 7 / W1.7 - Week 1 gate completion
- Starting point: Day 7 concept review, SQL debugging, and filtered endpoint implementation had passed; final milestone review remained.
- Concepts and work covered: Fresh-start setup rehearsal, setup guide review, project contract reconciliation, design snapshot reconciliation, and Week 1 architecture decision.
- Learner evidence: Earlier Day 7 evidence applies: learner answered the five review questions, debugged the aggregate query, and implemented the filtered endpoint. Fresh-start evidence was produced by running setup and validation in `C:\tmp\taskforge-fresh-20260911`.
- Files changed: `README.md`, `docs/project-contract.md`, `docs/design.md`, `docs/decisions.md`, `docs/tracker.md`, `docs/learning.md`, `docs/session-log.md`.
- Commands run and outcomes: Current workspace ruff check passed, format check passed, and pytest passed with `34 passed`. Fresh-start rehearsal created a clean venv, installed with `.\.venv\Scripts\python.exe -m pip install -e ".[dev]"`, then ruff check passed, format check passed, and pytest passed with `34 passed`.
- Problems and resolutions: README and project contract still referenced Day 6 and omitted `name_contains`; updated them. docs/design.md had a stale limitation and one literal newline escape; corrected both.
- Weak areas / incomplete work: Authentication, session security, real tenant authorization, readiness/dependency health, payload byte limits, live log inspection, and CI remain future work.
- Exact next action: Start Day 8 / W2.1 authentication and sessions when requested.
- Current repository state / relevant uncommitted work: Week 1 implementation and documentation changes remain uncommitted.

## 2026-09-11 - Day 8 / W2.1 - AuthRepository verification
- Starting point: Password/token helpers and sessions migration existed; AuthRepository tests initially covered only happy paths.
- Concepts and work covered: Active versus expired/revoked sessions, repository responsibility, and shared PostgreSQL test fixtures.
- Learner evidence: Learner added repository tests for expired sessions, revoked sessions, and missing session revocation.
- Files changed: `src/taskforge/auth_repository.py`, `tests/test_auth_repository.py`, `tests/conftest.py`, `tests/test_postgres_persistence.py`, Day 8 docs.
- Commands run and outcomes: `.\.venv\Scripts\python.exe -m pytest -q tests\test_auth_repository.py tests\test_postgres_persistence.py` passed with `10 passed` and two dependency warnings. Ruff check passed for auth repository and shared fixture files.
- Problems and resolutions: Importing a fixture from another test module passed pytest but failed Ruff as unused/redefined; moved the shared migrated PostgreSQL fixture into `tests/conftest.py`.
- Weak areas / incomplete work: AuthService, HTTP auth routes, cookie policy, CSRF, session rotation, and wrong-credential tests remain incomplete.
- Exact next action: Implement and test AuthService registration/login/logout/current-user behavior.
- Current repository state / relevant uncommitted work: Week 1 and Day 8 changes remain uncommitted.

## 2026-09-11 - Day 8 / W2.1 - Authentication completion
- Starting point: Session schema, security helpers, and AuthRepository were implemented and verified.
- Concepts and work covered: AuthService, login/logout/me/register routes, HttpOnly session cookies, CSRF token validation, expired/revoked sessions, and local HTTP versus production Secure-cookie behavior.
- Learner evidence: Earlier Day 8 concept answers apply: learner explained authentication vs authorization, password hashing vs encryption, CSRF risk, login/expiry/logout/session theft behavior, and repository tests for session states.
- Files changed: `src/taskforge/api.py`, `src/taskforge/auth_service.py`, `src/taskforge/auth_repository.py`, `src/taskforge/security.py`, `src/taskforge/errors.py`, `src/taskforge/models.py`, `src/taskforge/config.py`, `src/taskforge/db_models.py`, `migrations/versions/0002_add_sessions.py`, `tests/test_security.py`, `tests/test_auth_repository.py`, `tests/test_auth_api.py`, `tests/conftest.py`, README and docs.
- Commands run and outcomes: Focused auth suite passed with `14 passed`. Ruff check passed. Full pytest passed with `48 passed` and two dependency warnings.
- Problems and resolutions: CSRF dependency initially mapped the `CsrfError` class rather than an instance, producing 500 instead of 403; fixed and covered by API test.
- Weak areas / incomplete work: Project/task authorization and tenant isolation are not implemented; authentication alone does not prevent cross-user data access.
- Exact next action: Start Day 9 / W2.2 by writing an owner/admin/member/outsider permission matrix and then scoping project/task data paths to authenticated workspace membership.
- Current repository state / relevant uncommitted work: Week 1 and Day 8 implementation/documentation changes remain uncommitted.

## 2026-09-14 - Day 9 / W2.2 - Workspace-scoped project authorization
- Starting point: Day 9 concepts were checked, and workspace create/list/create-project authorization existed. Project item routes were not yet tenant-scoped.
- Concepts and work covered: Object-level authorization, tenant invisibility with `404`, same-tenant role denial with `403`, and repository lookups that bind user, workspace, and project together.
- Learner evidence: Earlier Day 9 evidence applies: learner corrected cross-tenant access to `404`, identified nested swap attacks, and separated authentication from authorization.
- Files changed: `src/taskforge/api.py`, `src/taskforge/errors.py`, `src/taskforge/authorization_repository.py`, `src/taskforge/authorization_service.py`, `tests/test_authorization.py`, `docs/tracker.md`, `docs/design.md`, `docs/decisions.md`, `docs/session-log.md`.
- Commands run and outcomes: Focused ruff check passed. `python -m pytest -q tests\test_authorization.py` passed with `11 passed`. Repository-wide ruff check passed, format check passed, and full pytest passed with `59 passed` and two dependency warnings.
- Problems and resolutions: A PowerShell replacement briefly wrote literal newline escapes into `src/taskforge/errors.py`; the file was immediately rewritten cleanly before validation.
- Weak areas / incomplete work: Task routes still need tenant-scoped parent-child authorization. Membership-management endpoints are not implemented; one member-role test inserts membership directly as setup.
- Exact next action: Add tenant-scoped task authorization tests and implementation for read/update/delete, including foreign project/task swap cases.
- Current repository state / relevant uncommitted work: Day 9 implementation and documentation changes are uncommitted; earlier Week 1 and Day 8 work also remains uncommitted.

## 2026-09-14 - Day 9 / W2.2 - Tenant-scoped task authorization
- Starting point: Workspace-scoped project authorization was implemented and validated. Task routes still used the legacy project-only path and did not prove workspace membership or parent-child ownership.
- Concepts and work covered: Tenant-scoped nested task lookups, parent-child checks, cross-tenant invisibility, and preserving service-level task status transition rules in the authorized path.
- Learner evidence: Earlier Day 9 evidence applies: learner identified both task swap attacks and expected `404` when the project/task does not belong to the current user's accessible workspace path.
- Files changed: `src/taskforge/api.py`, `src/taskforge/authorization_repository.py`, `src/taskforge/authorization_service.py`, `tests/test_authorization.py`, `docs/tracker.md`, `docs/design.md`, `docs/session-log.md`.
- Commands run and outcomes: Focused ruff check passed. `python -m pytest -q tests\test_authorization.py` passed with `18 passed`. Repository-wide ruff check passed, format check passed, and full pytest passed with `66 passed` and two dependency warnings.
- Problems and resolutions: Test setup needed a separate existing-user login helper when switching back to a previously registered owner; added `login_existing_user`.
- Weak areas / incomplete work: Membership-management endpoints are still missing. Legacy unauthenticated project/task routes still exist and need an explicit compatibility or removal decision.
- Exact next action: Decide whether to implement membership-management endpoints next or reconcile the legacy unauthenticated routes with the authenticated workspace route surface.
- Current repository state / relevant uncommitted work: Day 9 implementation and documentation changes are uncommitted; earlier Week 1 and Day 8 work also remains uncommitted.

## 2026-09-14 - Day 9 / W2.2 - Membership management endpoints
- Starting point: Workspace-scoped project and task authorization existed, but tests still needed direct database setup for membership roles and the API had no membership-management surface.
- Concepts and work covered: Role-based membership management, duplicate membership conflicts, in-tenant forbidden actions, outsider invisibility, and last-owner protection.
- Learner evidence: Earlier Day 9 evidence applies: learner supplied the role matrix and distinguished `404` cross-tenant invisibility from `403` in-tenant permission denial.
- Files changed: `src/taskforge/api.py`, `src/taskforge/models.py`, `src/taskforge/errors.py`, `src/taskforge/authorization_repository.py`, `src/taskforge/authorization_service.py`, `tests/test_authorization.py`, `docs/tracker.md`, `docs/design.md`, `docs/session-log.md`, `docs/decisions.md`.
- Commands run and outcomes: Focused authorization tests passed with `27 passed`. Repository-wide ruff check passed, format check passed, and full pytest passed with `75 passed` and two dependency warnings.
- Problems and resolutions: Tests initially reused an old CSRF token after logging the owner back in; fixed by using the fresh login result. Ruff also required import sorting in `src/taskforge/api.py`.
- Weak areas / incomplete work: Legacy unauthenticated project/task routes still exist and need explicit compatibility, migration, or removal handling.
- Exact next action: Decide how to handle legacy `/api/v1/projects...` routes now that authenticated workspace routes exist.
- Current repository state / relevant uncommitted work: Day 9 implementation and documentation changes are uncommitted; earlier Week 1 and Day 8 work also remains uncommitted.
## 2026-09-14 - Day 10 / W2.3 - Optimistic task concurrency
- Starting point: Day 9 authorization was complete, and task updates could still accept stale client snapshots without a version contract.
- Concepts and work covered: Lost updates, optimistic concurrency, version-checked writes, `409 Conflict`, and audit events committed with the task update.
- Learner evidence: Learner correctly explained the stale-version lost-update scenario and chose request-body `expected_version` with `409 Conflict` for TaskForge.
- Files changed: `migrations/versions/0003_task_versions_audit_events.py`, task models/repositories/services/API error mapping, concurrency tests, and Day 10 docs.
- Commands run and outcomes: Focused ruff check passed. Focused pytest for services, validation, project/task routes, authorization, and PostgreSQL persistence passed with `59 passed`. Full ruff check passed. Full ruff format check reported `41 files already formatted`. Full pytest passed with `78 passed` and two dependency deprecation warnings.
- Problems and resolutions: Authorization task updates initially referenced `AuditEventRow` without importing it; added the import and reran focused tests successfully.
- Weak areas / incomplete work: HTTP ETag/If-Match preconditions and row-lock experiments are deferred. No high-contention load test was run.
- Exact next action: Start Day 11 / W2.4 by inspecting query plans and adding a workload-driven index plus deterministic cursor pagination.
- Current repository state / relevant uncommitted work: Day 10 implementation and documentation changes are uncommitted along with prior roadmap work.
## 2026-09-14 - Day 11 / W2.4 - Task list cursor pagination and index evidence
- Starting point: Day 10 optimistic concurrency was complete. Task list queries were ordered by `created_at` only and had no cursor pagination contract.
- Concepts and work covered: Planner cost choice, selectivity, composite index order, offset cost, cursor pagination, deterministic tie-breakers, and EXPLAIN evidence.
- Learner evidence: Learner explained why PostgreSQL may ignore indexes, why `(project_id, created_at, id)` fits the task-list query, why offset work grows with page depth, and why `id` is required as a tie-breaker.
- Files changed: `migrations/versions/0004_add_task_list_cursor_index.py`, `src/taskforge/api.py`, `src/taskforge/repositories.py`, `src/taskforge/authorization_repository.py`, `src/taskforge/services.py`, `src/taskforge/authorization_service.py`, `src/taskforge/store.py`, `tests/test_postgres_persistence.py`, README and docs.
- Commands run and outcomes: Focused pytest passed with `50 passed`. Full pytest passed with `79 passed` and two dependency warnings. Ruff check and format check passed. Disposable `taskforge_day11` EXPLAIN plans showed cursor pagination using `ix_tasks_project_created_at_id` with 3 buffer hits, while `OFFSET 5000` scanned 5,020 rows and hit 101 buffers.
- Problems and resolutions: Initial manual Alembic run failed because `taskforge_day11` did not exist; created the database in the running `taskforge-postgres-1` container, then migrated successfully. A full pytest run transiently reported failures, but rerun passed with 79 tests.
- Weak areas / incomplete work: Opaque cursor tokens, additional sort modes, project-list cursor pagination, and concurrent pagination mutation behavior are deferred.
- Exact next action: Start Day 12 / W2.5 cache correctness by explaining cache-aside, invalidation timing, TTL, and stale-fill races.
- Current repository state / relevant uncommitted work: Day 11 implementation and documentation changes are uncommitted along with prior roadmap work.
