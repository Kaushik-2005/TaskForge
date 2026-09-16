# Backend Learning Tracker

## Current position
- Roadmap: roadmap.md
- Day / module: Day 13 / W2.6 Security and resource limits
- Calendar date: 2026-09-16
- Phase: Review
- Status: Completed
- Mode: Guided Learning
- Exact current task: Completed Day 13 Redis-backed rate limits for login, authenticated writes, and selected expensive reads.
- Last updated: 2026-09-16

## Day-by-day progress
| Day | Module | Date(s) | Implementation | Understanding | Overall |
| --- | --- | --- | --- | --- | --- |
| 1 | W1.1 | 2026-09-09 | Completed | Checked | Completed |
| 2 | W1.2 | 2026-09-09 | Completed | Checked | Completed |
| 3 | W1.3 | 2026-09-09 | Completed | Checked | Completed |
| 4 | W1.4 | 2026-09-09 | Completed | Checked | Completed |
| 5 | W1.5 | 2026-09-10 | Completed | Checked | Completed |
| 6 | W1.6 | 2026-09-10 | Completed | Checked | Completed |
| 7 | W1.7 | 2026-09-11 | Completed | Checked | Completed |
| 8 | W2.1 | 2026-09-11 | Completed | Checked | Completed |
| 9 | W2.2 | 2026-09-13 to 2026-09-14 | Completed | Checked | Completed |
| 10 | W2.3 | 2026-09-14 | Completed | Checked | Completed |
| 11 | W2.4 | 2026-09-14 | Completed | Checked | Completed |
| 12 | W2.5 | 2026-09-16 | Completed | Checked | Completed |
| 13 | W2.6 | 2026-09-16 | Completed | Checked | Completed |
| 14 | W2.7 | - | Not started | Not checked | Not started |
| 15 | W3.1 | - | Not started | Not checked | Not started |
| 16 | W3.2 | - | Not started | Not checked | Not started |
| 17 | W3.3 | - | Not started | Not checked | Not started |
| 18 | W3.4 | - | Not started | Not checked | Not started |
| 19 | W3.5 | - | Not started | Not checked | Not started |
| 20 | W3.6 | - | Not started | Not checked | Not started |
| 21 | W3.7 | - | Not started | Not checked | Not started |
| 22 | W4.1 | - | Not started | Not checked | Not started |
| 23 | W4.2 | - | Not started | Not checked | Not started |
| 24 | W4.3 | - | Not started | Not checked | Not started |
| 25 | W4.4 | - | Not started | Not checked | Not started |
| 26 | W4.5 | - | Not started | Not checked | Not started |
| 27 | W4.6 | - | Not started | Not checked | Not started |
| 28 | W4.7 | - | Not started | Not checked | Not started |

## Current module evidence
- [x] Required selected reading completed or explained with source
- [x] Core concept explained by learner
- [x] Knowledge check passed
- [x] Exercise attempted and reviewed
- [x] Required project increment or design/lab completed
- [x] Relevant validation executed
- [x] Notes and corrections saved
- [x] Daily design entry and current architecture snapshot reviewed
- Reading/sections: Day 13 used BFP 17 security/abuse concepts, BFP 01 CORS distinction, OWASP authorization context, and Redis atomic counter behavior as the source map.
- Learner answer or concise evidence: Learner correctly explained that CORS is browser-enforced and does not stop curl/scripts; identified login, writes, and expensive reads as rate-limit targets; and explained why login is fail-closed while authenticated reads/writes are fail-open.
- Exercise path/result: Initial policy defined and implemented: login by IP+email is 5/min fail-closed; authenticated writes by user are 60/min fail-open; selected expensive authenticated reads by user are 30/min fail-open.
- Changed files: `src/taskforge/rate_limit.py`, `src/taskforge/main.py`, `src/taskforge/api.py`, `tests/test_rate_limit.py`, `tests/test_auth_api.py`, `tests/test_authorization.py`, and Day 13 docs.
- Commands and actual results: `\.venv\Scripts\python.exe -m ruff check .` passed; `\.venv\Scripts\python.exe -m pytest -q tests` passed with `99 passed`, two dependency deprecation warnings.
- Design entry / related ADRs: `docs/design.md` Day 13 entry; ADR-010 records Redis-backed rate-limit policy and fail-open/fail-closed choices.
- Untested assumptions: No multi-process live Redis race test, trusted proxy/IP parsing policy, production load tuning, or global request body byte-size middleware yet.
- Weak concepts: None blocking; continue reinforcing that rate limiting is not authorization and CORS is not a server-side security boundary.
- Optional work deferred: Configurable per-route limits, proxy-aware client IP handling, rate-limit metrics, broader read-route coverage, payload byte-size limits, and login account lockout policy.
## Last completed module evidence - Day 12
- [x] Required selected reading completed or explained with source
- [x] Core concept explained by learner
- [x] Knowledge check passed
- [x] Exercise attempted and reviewed
- [x] Required project increment or design/lab completed
- [x] Relevant validation executed
- [x] Notes and corrections saved
- [x] Daily design entry and current architecture snapshot reviewed
- Reading/sections: Day 12 used BFP 09 cache concepts and Redis cache-aside behavior as the source map; implementation notes focused on cache-aside, TTL, invalidation, tenant-scoped keys, and Redis outage behavior.
- Learner answer or concise evidence: Learner explained the stale-fill race, why TTL and invalidation solve different failure modes, why cache keys must include `workspace_id`, and why Redis is a disposable optimization while PostgreSQL remains authoritative.
- Exercise path/result: Stale-fill and invalidation exercise completed; TaskForge now uses a 30-second TTL plus post-commit invalidation for project summaries.
- Changed files: `pyproject.toml`, `compose.yaml`, `src/taskforge/cache.py`, `src/taskforge/config.py`, `src/taskforge/main.py`, `src/taskforge/api.py`, `src/taskforge/models.py`, `src/taskforge/authorization_repository.py`, `src/taskforge/authorization_service.py`, `tests/test_cache.py`, `tests/test_authorization.py`, and Day 12 docs.
- Commands and actual results: Focused `pytest` for cache and authorization passed with `39 passed`; `ruff check .` passed; learner reported full tests and format checks passed; manual `docker compose exec redis redis-cli ping` returned `PONG`.
- Design entry / related ADRs: `docs/design.md` Day 12 entry; ADR-009 records the cache-aside Redis project summary decision.
- Untested assumptions: No high-concurrency stale-fill race test, cache stampede test, hot-key load test, or production Redis outage-duration test was run.
- Weak concepts: None blocking; stale-fill is understood as a bounded freshness limitation rather than a fully eliminated race.
- Optional work deferred: Stampede protection, opaque cache version bump strategy, Redis readiness checks, and broader cached read models.

## Last completed module evidence - Day 11 / W2.4
- [x] Required selected reading completed or explained with source
- [x] Core concept explained by learner
- [x] Knowledge check passed
- [x] Exercise attempted and reviewed
- [x] Required project increment or design/lab completed
- [x] Relevant validation executed
- [x] Notes and corrections saved
- [x] Daily design entry and current architecture snapshot reviewed
- Reading/sections: BFP 08 indexes, BFP 18 database bottlenecks, and PostgreSQL EXPLAIN documentation.
- Learner answer or concise evidence: Learner correctly explained planner cost choice, why a composite `(project_id, created_at, id)` index matches the query better than separate indexes, why `OFFSET` gets slower with deeper pages, and why `id` is needed as a tie-breaker.
- Exercise path/result: Seeded 10,000 tasks in disposable `taskforge_day11`; compared indexed first-page, cursor, and `OFFSET 5000` plans with `EXPLAIN (ANALYZE, BUFFERS)`.
- Changed files: `migrations/versions/0004_add_task_list_cursor_index.py`, `src/taskforge/api.py`, `src/taskforge/repositories.py`, `src/taskforge/authorization_repository.py`, `src/taskforge/services.py`, `src/taskforge/authorization_service.py`, `src/taskforge/store.py`, `tests/test_postgres_persistence.py`, docs and contract files.
- Commands and actual results: `python -m ruff check .` passed; `python -m ruff format --check .` passed; focused pytest passed with `50 passed`; full pytest passed with `79 passed`, two dependency deprecation warnings.
- Design entry / related ADRs: `docs/design.md` Day 11 entry updated; ADR-008 records cursor pagination and composite index decision.
- Untested assumptions: No production-sized workload, concurrent pagination mutation scenario, or alternate sort allowlist was tested.
- Weak concepts: Continue reinforcing that indexes are workload-shaped and planner-selected, not automatically used.
- Optional work deferred: Encoded opaque cursor tokens and additional sort modes are deferred.
## Last completed module evidence - Day 10 / W2.3
- [x] Required selected reading completed or explained with source
- [x] Core concept explained by learner
- [x] Knowledge check passed
- [x] Exercise attempted and reviewed
- [x] Required project increment or design/lab completed
- [x] Relevant validation executed
- [x] Notes and corrections saved
- [x] Daily design entry and current architecture snapshot reviewed
- Reading/sections: Day 10 used BFP 08 transactions, BFP 20 races, and PostgreSQL transaction isolation documentation as the conceptual source map.
- Learner answer or concise evidence: Learner correctly explained the lost-update risk when two users edit from the same stale version and chose an `expected_version` request-body contract with `409 Conflict` for stale writes.
- Exercise path/result: Added version-checked task updates and PostgreSQL tests proving a stale writer cannot silently overwrite the first writer.
- Changed files: `migrations/versions/0003_task_versions_audit_events.py`, `src/taskforge/db_models.py`, `src/taskforge/models.py`, `src/taskforge/errors.py`, `src/taskforge/store.py`, `src/taskforge/repositories.py`, `src/taskforge/authorization_repository.py`, `src/taskforge/services.py`, `src/taskforge/authorization_service.py`, `src/taskforge/api.py`, `tests/test_postgres_persistence.py`, `tests/test_authorization.py`, `tests/test_projects_tasks.py`, `tests/test_services.py`, `tests/test_validation.py`, docs and contract files.
- Commands and actual results: `./.venv/Scripts/python.exe -m ruff check .` passed; `./.venv/Scripts/python.exe -m ruff format --check .` reported 41 files already formatted; focused Day 10 pytest passed with `59 passed`; full pytest passed with `78 passed`, two dependency deprecation warnings.
- Design entry / related ADRs: `docs/design.md` Day 10 entry updated; ADR-007 records version-based optimistic concurrency.
- Untested assumptions: No high-contention load test or deadlock experiment yet; Day 10 proves the stale-write contract, not broad production concurrency behavior.
- Weak concepts: Continue reinforcing that a database transaction alone does not make stale client snapshots safe.
- Optional work deferred: HTTP `If-Match`/ETag precondition contract and explicit row-locking comparison are deferred.
## Weekly gates
- [x] Week 1: Durable validated CRUD
- [ ] Week 2: Isolated multi-user API
- [ ] Week 3: Recoverable background work
- [ ] Week 4: Operated release and capstone

## Blockers and deviations
- Git status could not be inspected because the folder is not a Git repository. Impact: no version-control diff evidence yet. Recovery action: initialize or connect Git when the learner wants repository tracking. Return point: Day 2 startup.
- The normal patch tool and some sandboxed commands failed because `codex-windows-sandbox-setup.exe` was unavailable. Recovery action: local workspace edits and validation were run with explicit escalation.

## Exact next session
- Module and phase: Day 14 / W2.7, Orient
- File/function/section: Week 2 correctness review; security/race/cache scenario pack
- Next question or exercise: Answer five review questions covering identity, permissions, transactions, indexes, caching, and rate limits.
- Next build task: Build or verify the Day 14 scenario pack: expired session, swapped workspace IDs, stale version, DB rollback, Redis outage, oversized input, and rate-limit behavior.
- Next validation command: `\.venv\Scripts\python.exe -m ruff check .` and `\.venv\Scripts\python.exe -m pytest -q tests`