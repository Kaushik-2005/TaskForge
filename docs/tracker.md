# Backend Learning Tracker

## Current position
- Roadmap: roadmap.md
- Day / module: Day 11 / W2.4 Indexes and query performance
- Calendar date: 2026-09-14
- Phase: Orient
- Status: Not Started
- Mode: Guided Learning
- Exact current task: Start Day 11 by learning query plans, index selectivity, composite index order, and cursor pagination.
- Last updated: 2026-09-14

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
| 11 | W2.4 | - | Not started | Not checked | Not started |
| 12 | W2.5 | - | Not started | Not checked | Not started |
| 13 | W2.6 | - | Not started | Not checked | Not started |
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
- [ ] Required selected reading completed or explained with source
- [ ] Core concept explained by learner
- [ ] Knowledge check passed
- [ ] Exercise attempted and reviewed
- [ ] Required project increment or design/lab completed
- [ ] Relevant validation executed
- [ ] Notes and corrections saved
- [ ] Daily design entry and current architecture snapshot reviewed
- Reading/sections: Day 11 will use BFP 08 index/query-plan sections, BFP 18 database bottlenecks, and PostgreSQL EXPLAIN documentation.
- Learner answer or concise evidence: Pending Day 11 index and query-plan explanation.
- Exercise path/result: Pending larger dataset and EXPLAIN exercise.
- Changed files: Pending Day 11.
- Commands and actual results: Pending Day 11.
- Design entry / related ADRs: Pending Day 11 query-performance design entry.
- Untested assumptions: Need to measure current list/search queries before adding indexes.
- Weak concepts: Planner choices, selectivity, composite index order, and cursor pagination are not checked yet.
- Optional work deferred: None yet.
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
- Module and phase: Day 11 / W2.4, Orient
- File/function/section: PostgreSQL `EXPLAIN`, project/task list queries, pagination/index design
- Next question or exercise: Explain why an index can speed a selective lookup but may be ignored by the planner for low-selectivity or small-table queries.
- Next build task: Seed a larger task dataset, inspect query plans, add one workload-driven index, and introduce deterministic cursor pagination.
- Next validation command: `.\.venv\Scripts\python.exe -m pytest -q` plus Day 11 query-plan evidence commands
