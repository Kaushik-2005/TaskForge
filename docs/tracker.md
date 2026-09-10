# Backend Learning Tracker

## Current position
- Roadmap: roadmap.md
- Day / module: Day 6 / W1.6 Persistence and migrations
- Calendar date: 2026-09-10
- Phase: Review
- Status: Completed
- Mode: Guided Learning
- Exact current task: Day 6 completed; next action is to start Day 7 foundation review only when requested.
- Last updated: 2026-09-10

## Day-by-day progress
| Day | Module | Date(s) | Implementation | Understanding | Overall |
| --- | --- | --- | --- | --- | --- |
| 1 | W1.1 | 2026-09-09 | Completed | Checked | Completed |
| 2 | W1.2 | 2026-09-09 | Completed | Checked | Completed |
| 3 | W1.3 | 2026-09-09 | Completed | Checked | Completed |
| 4 | W1.4 | 2026-09-09 | Completed | Checked | Completed |
| 5 | W1.5 | 2026-09-10 | Completed | Checked | Completed |
| 6 | W1.6 | 2026-09-10 | Completed | Checked | Completed |
| 7 | W1.7 | - | Not started | Not checked | Not started |
| 8 | W2.1 | - | Not started | Not checked | Not started |
| 9 | W2.2 | - | Not started | Not checked | Not started |
| 10 | W2.3 | - | Not started | Not checked | Not started |
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
- [x] Required selected reading completed or explained with source
- [x] Core concept explained by learner
- [x] Knowledge check passed
- [x] Exercise attempted and reviewed
- [x] Required project increment or design/lab completed
- [x] Relevant validation executed
- [x] Notes and corrections saved
- [x] Daily design entry and current architecture snapshot reviewed
- Reading/sections: Day 6 assigned readings are BFP 08 database access and BFP 22 integration tests/fixtures; to cover connection pools, request-scoped sessions, commit/rollback, migrations, N+1 awareness, and isolated test databases.
- Learner answer or concise evidence: Learner correctly explained that a multi-step request should be atomic and that repositories should generally add/flush while one commit happens at the request/service transaction boundary after the whole service operation succeeds. Learner also correctly calculated pool demand as `(pool_size + max_overflow) * worker_processes`, e.g. `(5 + 2) * 4 = 28`, because each process owns its own pool.
- Exercise path/result: Learner explained that internal repository commits can leave project committed and task 1 committed when task 2 fails, and correctly distinguished flush from commit: flush sends SQL inside the current transaction while commit makes the transaction permanent.
- Changed files: `.env.example`, `README.md`, `alembic.ini`, `migrations/env.py`, `migrations/versions/0001_initial_schema.py`, `pyproject.toml`, `src/taskforge/api.py`, `src/taskforge/config.py`, `src/taskforge/db.py`, `src/taskforge/db_models.py`, `src/taskforge/main.py`, `src/taskforge/repositories.py`, `src/taskforge/services.py`, existing memory-backed tests, `tests/test_postgres_persistence.py`, and Day 6 docs.
- Commands and actual results: Dependencies installed with `.\.venv\Scripts\python.exe -m pip install -e ".[dev]"`. Final validation: `.\.venv\Scripts\python.exe -m ruff check .` passed; `.\.venv\Scripts\python.exe -m ruff format --check .` passed; `.\.venv\Scripts\python.exe -m pytest -q` passed with `28 passed` and two dependency warnings. PostgreSQL integration tests created and dropped isolated temporary databases. Manual test also verified creating a project through the API, stopping Uvicorn, restarting Uvicorn, and listing the same project from PostgreSQL-backed storage.
- Design entry / related ADRs: ADR-003 accepted; docs/design.md Day 6 entry added with a PostgreSQL request sequence diagram.
- Untested assumptions: Developer `taskforge` database may still contain Day 5 manual schema without an Alembic version table; use fresh database or deliberate migration stamping before relying on Alembic there.
- Weak concepts: Continue reinforcing migration state on existing databases and test isolation trade-offs during Day 7 review.
- Optional work deferred: Full authenticated workspace scoping; N+1 query performance lab; explicit production migration/runbook workflow.
## Weekly gates
- [ ] Week 1: Durable validated CRUD
- [ ] Week 2: Isolated multi-user API
- [ ] Week 3: Recoverable background work
- [ ] Week 4: Operated release and capstone

## Blockers and deviations
- Git status could not be inspected because the folder is not a Git repository. Impact: no version-control diff evidence yet. Recovery action: initialize or connect Git when the learner wants repository tracking. Return point: Day 2 startup.
- The normal patch tool and some sandboxed commands failed because `codex-windows-sandbox-setup.exe` was unavailable. Recovery action: local workspace edits and validation were run with explicit escalation.

## Exact next session
- Module and phase: Day 7 / W1.7, Orient
- File/function/section: roadmap.md Day 7; Week 1 API, service, validation, database, migration, and test boundaries
- Next question or exercise: Five-question Week 1 foundation review, then debug a broken query and implement a small filtered endpoint.
- Next build task: Day 7 foundation review task after concept questions.
- Next validation command: `.\.venv\Scripts\python.exe -m pytest -q`














