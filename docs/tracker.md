# Backend Learning Tracker

## Current position
- Roadmap: roadmap.md
- Day / module: Day 23 / W4.2 Load and capacity
- Calendar date: 2026-09-28
- Phase: Review
- Status: Completed
- Mode: Guided Learning
- Exact current task: Day 23 complete; begin Day 24 scaling trade-offs when requested.
- Last updated: 2026-09-28

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
| 14 | W2.7 | 2026-09-17 | Completed | Checked | Completed |
| 15 | W3.1 | 2026-09-22 | Completed | Checked | Completed |
| 16 | W3.2 | 2026-09-22 | Completed | Checked | Completed |
| 17 | W3.3 | 2026-09-22 to 2026-09-23 | Completed | Checked | Completed |
| 18 | W3.4 | 2026-09-23 | Completed | Checked | Completed |
| 19 | W3.5 | 2026-09-27 | Completed | Checked | Completed |
| 20 | W3.6 | 2026-09-27 to 2026-09-28 | Completed | Checked | Completed |
| 21 | W3.7 | 2026-09-28 | Completed | Checked | Completed |
| 22 | W4.1 | 2026-09-28 | Completed | Checked | Completed |
| 23 | W4.2 | 2026-09-28 | Completed | Checked | Completed |
| 24 | W4.3 | - | Not started | Not checked | Not started |
| 25 | W4.4 | - | Not started | Not checked | Not started |
| 26 | W4.5 | - | Not started | Not checked | Not started |
| 27 | W4.6 | - | Not started | Not checked | Not started |
| 28 | W4.7 | - | Not started | Not checked | Not started |

## Last completed module evidence - Day 15
- [x] Required selected reading completed or explained with source
- [x] Core concept explained by learner
- [x] Knowledge check passed
- [x] Exercise attempted and reviewed
- [x] Required project increment or design/lab completed
- [x] Relevant validation executed
- [x] Notes and corrections saved
- [x] Daily design entry and current architecture snapshot reviewed
- Reading/sections: Day 15 / W3.1, BFP 10 queue/job lifecycle; durable acceptance, polling/status lookup, claim/complete, terminal failure, and process-local callback limitations.
- Learner answer or concise evidence: Learner correctly explained that `202 Accepted` must follow the transaction committing the export/job records. Learner identified the lost-work risk when the response precedes commit, the ambiguous outcome when a crash follows commit but precedes the response, and the role of an idempotency key in safe retry.
- Exercise path/result: Learner mapped pending/running/succeeded/failed crash boundaries and identified durable claim identity, attempt count, lease expiry, retry limits, and output reconciliation needs. Learner then designed a minimal PostgreSQL `jobs`/`exports` model, an atomic acceptance transaction, authorized status lookup, and a one-worker claim/complete flow. Review corrections: lease expiry removes trusted ownership but does not prove the old worker stopped; completion must be conditional on the current ownership token. Duplicate status fields need an explicit synchronization invariant, and find-then-claim is only safe under the one-worker assumption.
- Changed files: `migrations/versions/0005_add_exports_and_jobs.py`, `src/taskforge/db_models.py`, `src/taskforge/jobs.py`, `src/taskforge/worker.py`, `src/taskforge/models.py`, `src/taskforge/api.py`, `src/taskforge/config.py`, `src/taskforge/errors.py`, `tests/test_jobs.py`, `README.md`, and learning/design/session records.
- Commands and actual results: Focused Day 15 tests passed with `4 passed` after the worker entry-point addition; full `\.venv\Scripts\python.exe -m pytest -q tests` passed with `104 passed` before the entry-point-only change and two dependency deprecation warnings; `\.venv\Scripts\python.exe -m ruff check .` passed; final format check reported 45 files already formatted; `python -m taskforge.worker --help` passed.
- Design entry / related ADRs: `docs/design.md` Day 15 entry; no new ADR because this is the first bounded PostgreSQL job implementation and lease/idempotency decisions remain deferred to Days 16–17.
- Untested assumptions: The one-worker find-then-claim flow is not safe for multiple workers. There are no leases, ownership tokens, retry limits, idempotency keys, crash-recovery reconciliation, or download endpoint yet. Local output storage is a learning implementation, not a release storage policy. Worker exceptions are intentionally reduced to a generic client-safe failure message; structured worker logging is deferred.
- Weak concepts: Continue reinforcing that lease expiry is not proof of worker termination and that repeated execution remains possible when leases and idempotency are added.
- Optional work deferred: Broker/outbox design is outside today's core build and will remain a comparison topic unless the roadmap requires it.

## Last completed module evidence - Day 16
- [x] Required selected reading completed or explained with source
- [x] Core concept explained by learner
- [x] Knowledge check passed
- [x] Exercise attempted and reviewed
- [x] Required project increment or design/lab completed
- [x] Relevant validation executed
- [x] Notes and corrections saved
- [x] Daily design entry and current architecture snapshot reviewed
- Reading/sections: Day 16 / W3.2, BFP 20 concurrency and parallelism; BFP 16 cancellation basics; async event-loop and bounded-concurrency concepts.
- Learner answer or concise evidence: Learner correctly explained that claims must commit before slow work, that slow work must occur outside the claim transaction, and that lease expiry means ownership is stale rather than proving worker termination or side-effect absence. Learner also correctly distinguished I/O-bound concurrency from CPU-bound Python work under the GIL and identified the need to bound concurrency against database, CPU, memory, file, and downstream capacity. Precision correction recorded: with `FOR UPDATE SKIP LOCKED`, another worker skips an uncommitted locked row; without that clause it may observe the previous committed state.
- Exercise path/result: Sequential async waits took 1.60s; bounded concurrency of 2 took 0.80s with maximum active count 2; blocking `time.sleep()` event-loop demonstration was completed. Added atomic claim, leases, renewal heartbeat, ownership-token conditional completion, expiry reclaim, and bounded ThreadPoolExecutor worker tests.
- Changed files: `migrations/versions/0006_add_job_leases.py`, `src/taskforge/db_models.py`, `src/taskforge/config.py`, `src/taskforge/jobs.py`, `src/taskforge/worker.py`, `tests/test_jobs.py`, and learning/design/session records.
- Commands and actual results: Focused Day 16 job tests passed with `6 passed`; full `\.venv\Scripts\python.exe -m pytest -q tests` passed with `106 passed` and two dependency deprecation warnings; `\.venv\Scripts\python.exe -m ruff check .` passed; final format check reported 46 files already formatted.
- Design entry / related ADRs: `docs/design.md` Day 16 entry; no new ADR because the implementation follows the roadmap's PostgreSQL claim mechanism and lease decision remains bounded to the worker lab.
- Untested assumptions: No live process-kill/restart recovery experiment, multi-process load test, or measured lease/concurrency tuning was run. A worker that loses its lease may still produce an orphan output; idempotent artifact finalization is deferred to Day 17. CPU-heavy work is not moved to a process pool.
- Weak concepts: Continue reinforcing that lease expiry does not stop execution and that process-local locks cannot coordinate separate worker processes.
- Optional work deferred: Process-pool CPU execution, adaptive concurrency, lease metrics, and live failure injection.

## Last completed module evidence - Day 20 / W3.6
- [x] Required selected reading completed or explained with source
- [x] Core concept explained by learner
- [x] Knowledge check passed
- [x] Exercise attempted and reviewed
- [x] Required project increment or design/lab completed
- [x] Relevant validation executed
- [x] Notes and corrections saved
- [x] Daily design entry and current architecture snapshot reviewed
- Reading/sections: Day 20 / W3.6, BFP 24 connection/backpressure; BFP 13 contracts; BFP 23 ordering/replay; gRPC deadlines; Kafka design.
- Learner answer or concise evidence: Learner selected SSE for one-way export status, WebSocket for interactive workspace updates, and durable events for worker-to-worker completion. Learner designed `task.updated` with per-task monotonic versioning and correctly explained reconnect/refetch from PostgreSQL.
- Exercise path/result: Implemented initial in-process WebSocket/broker lab; protocol comparison and event-ordering exercise reviewed.
- Changed files: `src/taskforge/realtime.py`, `src/taskforge/api.py`, `src/taskforge/config.py`, `src/taskforge/main.py`, `tests/test_realtime.py`.
- Commands and actual results: Learner reported that `python -m ruff check .`, `python -m ruff format --check .`, focused real-time tests, and `python -m pytest -q tests` all passed.
- Design entry / related ADRs: Day 20 design entry added; no production real-time ADR yet.
- Untested assumptions: Real task-mutation publication, cancellation under abrupt disconnect, and multi-instance delivery remain unverified.
- Weak concepts: Durable event publication/outbox and cross-instance replay remain deferred.
- Optional work deferred: gRPC/Kafka deployment and cross-instance event delivery remain comparison topics.

## Current module evidence - Day 21 / W3.7
- [ ] Required selected reading completed or explained with source
- [x] Core concept explained by learner
- [x] Knowledge check passed
- [x] Exercise attempted and reviewed
- [x] Required project increment or design/lab completed
- [x] Relevant validation executed
- [x] Notes and corrections saved
- [x] Daily design entry and current architecture snapshot reviewed
- Reading/sections: Day 21 recovery review; no new reading assigned yet.
- Learner answer or concise evidence: Learner correctly explained lease-expiry uncertainty, idempotency-key plus request-fingerprint replay, bounded single-owner retries, SQL tenant scoping, and reconnect/refetch from PostgreSQL after WebSocket loss.
- Exercise path/result: Diagnosed expired-lease reclamation, added a regression test for cleanup after fenced completion is rejected, and added a controlled worker-restart recovery test.
- Changed files: `tests/test_jobs.py` and Day 21 records.
- Commands and actual results: Learner reported focused recovery validation with `27 passed`, controlled restart validation with `1 passed`, and the final `ruff check`, `ruff format --check`, and full pytest gate passed.
- Design entry / related ADRs: Day 21 design entry; no new ADR yet.
- Untested assumptions: An actual OS process kill during CSV generation, multi-instance recovery, and production storage cleanup remain unverified; the controlled test covers durable expired-claim recovery.
- Weak concepts: None identified in the five-question review; continue distinguishing stale ownership from proof of worker termination.
- Optional work deferred: Broader exactly-once and losslessness claims remain out of scope.

## Last completed module evidence - Day 22 / W4.1
- [x] Required selected reading completed or explained with source
- [x] Core concept explained by learner
- [x] Knowledge check passed
- [x] Exercise attempted and reviewed
- [x] Required project increment or design/lab completed
- [x] Relevant validation executed
- [x] Notes and corrections saved
- [x] Daily design entry and current architecture snapshot reviewed
- Reading/sections: OpenTelemetry signals and Google SRE service-level objectives.
- Learner answer or concise evidence: Learner correctly diagnosed rising queue age with normal SQL latency as a likely worker/queue capacity or health bottleneck, selected worker utilization/throughput/execution duration as next signals, chose bounded route/method/status labels over high-cardinality identifiers, explained why p99 exposes user-visible tail latency hidden by averages, and defined a valid 99.9%/500 ms/30-day export-status SLO with a narrow 401 exclusion.
- Exercise path/result: Signal-selection, metric-cardinality, tail-latency, and SLI/SLO definition exercises completed; implemented the first bounded HTTP metrics increment.
- Changed files: `src/taskforge/observability.py`, `src/taskforge/main.py`, `tests/test_app_boundaries.py`, and Day 22 records.
- Commands and actual results: Focused observability boundary tests passed with `7 passed`; the learner reported Ruff check, Ruff format check, and the full pytest suite all passed.
- Design entry / related ADRs: Day 22 design entry; no new ADR yet.
- Untested assumptions: Trace correlation, database/cache/job instrumentation, metric export, and measured SLO reporting.
- Weak concepts: Metric labels, histogram tails, sampling, and error-budget policy remain to be checked.
- Optional work deferred: Production telemetry backend selection, dashboards, and alert routing remain deferred.

## Current module evidence - Day 23 / W4.2
- [ ] Required selected reading completed or explained with source
- [x] Core concept explained by learner
- [x] Knowledge check passed
- [x] Exercise attempted and reviewed
- [x] Required project increment or design/lab completed
- [x] Relevant validation executed
- [x] Notes and corrections saved
- [x] Daily design entry and current architecture snapshot reviewed
- Reading/sections: Day 23 load, capacity, queueing, and measurement.
- Learner answer or concise evidence: Learner correctly applied Little's Law to estimate 20 in-flight exports and explained why unbounded queues turn arrival-rate overload into growing wait time, resource use, and stale work. Learner proposed a reproducible 20-workspace/400-project/40,000-task dataset, a 70/20/10 read-write-export mix, 50-user gradual ramp, and cold/warm cache comparison.
- Exercise path/result: Load-model concept exercise and baseline workload specification completed; environment capture completed, an authenticated Locust workload was implemented, and a repeatable fixed-dataset seeder with automatic PowerShell environment-file generation was added.
- Changed files: `load_tests/locustfile.py`, `load_tests/README.md`, `scripts/seed_load_data.py`, `pyproject.toml`, `docs/performance-report.md`, and Day 23 records.
- Commands and actual results: Captured Python 3.12.0, PostgreSQL 17.11, Redis 7.4.11, worker concurrency 2, and initial database pool size 5 with max overflow 0. The existing five-table schema was stamped at `0001_initial_schema` and upgraded successfully to the current Alembic head. Earlier smoke attempts failed due to API startup, missing variables, and invalid credentials; the corrected smoke test passed with `6 requests`, `0 failures`, and exit code 0. The first 50-user run exposed pool exhaustion (`QueuePool limit of size 5 overflow 0`); with pool size 20 and max overflow 10, the baseline completed with 17,933 requests, 6 failures (`0.03%`), 27.1 requests/sec, aggregate p50 37 ms, p95 77 ms, p99 130 ms, p99.9 1,200 ms, and maximum 1,600 ms.
- Design entry / related ADRs: Day 23 design entry updated with the measured pool bottleneck and bounded pool tuning; no new ADR yet.
- Untested assumptions: The six baseline failures were five `401` task-list responses and one `429` task-list response; the `429` is consistent with the existing read-rate policy, and the `401` investigation was explicitly deferred. The cold-cache run completed with 17,854 requests, 3 rate-limit failures, 24.88 requests/sec, p50 48 ms, p95 150 ms, p99 250 ms, p99.9 390 ms, and maximum 700 ms. The warm-cache run completed with 17,660 requests, 58 failures (`0.33%`), 24.53 requests/sec, p50 41 ms, and maximum 7,997 ms; failures included 22 export-status `404`s and 36 task/export `500`s, whose causes were deferred. Resource measurements, queue age, and a bottleneck rerun remain pending. Seeder lint/format could not be run in the agent shell because its virtual-environment interpreter is unavailable.
- Weak concepts: To be identified during the Day 23 review.
- Optional work deferred: None selected yet.

## 2026-09-28 - Day 23 / W4.2 completion note
- Implementation evidence: Deterministic load seeder, authenticated Locust workload, pool bottleneck experiment, pool-20 rerun, cold-cache run, warm-cache run, queue/export measurements, and performance report completed.
- Validation evidence: `python -m ruff check .`, `python -m ruff format --check .`, and `python -m pytest -q` all passed.
- Deferred limitations: Five baseline task-list `401`s, warm-run `404`/`500` causes, peak rather than post-run resource measurements, and time-series pool-wait metrics remain unresolved or incomplete.
- Exact next session: Start Day 24 / W4.3 scaling trade-offs.

## Last completed module evidence - Day 13
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
- [x] Week 2: Isolated multi-user API
- [x] Week 3: Recoverable background work
- [ ] Week 4: Operated release and capstone

## Blockers and deviations
- Git status could not be inspected because the folder is not a Git repository. Impact: no version-control diff evidence yet. Recovery action: initialize or connect Git when the learner wants repository tracking. Return point: Day 2 startup.
- The normal patch tool and some sandboxed commands failed because `codex-windows-sandbox-setup.exe` was unavailable. Recovery action: local workspace edits and validation were run with explicit escalation.

## Exact next session
- Module and phase: Day 22 / W4.1, Orient
- File/function/section: Observability signals, traces, metrics, and SLO definitions.
- Next question or exercise: Distinguish logs, metrics, and traces for locating request, database, queue, and dependency delay.
- Next build task: Inspect the Day 22 requirements before changing runtime code.
- Next validation command: Select the focused Day 22 observability check after orientation.
