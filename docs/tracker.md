# Backend Learning Tracker

## Current position
- Roadmap: roadmap.md
- Day / module: Day 4 / W1.4 Layers and configuration
- Calendar date: 2026-09-09
- Phase: Review
- Status: Completed
- Mode: Guided Learning
- Exact current task: Day 4 core requirements completed; next action is to start Day 5 only when requested.
- Last updated: 2026-09-09

## Day-by-day progress
| Day | Module | Date(s) | Implementation | Understanding | Overall |
| --- | --- | --- | --- | --- | --- |
| 1 | W1.1 | 2026-09-09 | Completed | Checked | Completed |
| 2 | W1.2 | 2026-09-09 | Completed | Checked | Completed |
| 3 | W1.3 | 2026-09-09 | Completed | Checked | Completed |
| 4 | W1.4 | 2026-09-09 | Completed | Checked | Completed |
| 5 | W1.5 | - | Not started | Not checked | Not started |
| 6 | W1.6 | - | Not started | Not checked | Not started |
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
- Reading/sections: Day 4 assigned readings were BFP 06 controllers/services/middleware, BFP 14 settings precedence/startup validation, and BFP 12 error classification. Covered route/service/store ownership, exception mapping, request ID middleware, structured logs, and startup config validation.
- Learner answer or concise evidence: Learner correctly placed the task status transition rule in the service layer. Learner initially placed validation error-envelope behavior in route handlers, then corrected that invalid UUID validation fails before the route handler runs and should be mapped by exception handling. Learner traced a `todo -> done` task update through route parsing, service rule enforcement, store update only after approval, error mapping, and expected `409 Conflict`.
- Exercise path/result: Task-update trace exercise completed and reviewed.
- Changed files: `README.md`, `.env.example`, `docs/project-contract.md`, `docs/tracker.md`, `docs/learning.md`, `docs/design.md`, `docs/session-log.md`, `docs/decisions.md`, `src/taskforge/api.py`, `src/taskforge/config.py`, `src/taskforge/errors.py`, `src/taskforge/main.py`, `src/taskforge/services.py`, `src/taskforge/store.py`, `tests/test_app_boundaries.py`, `tests/test_services.py`.
- Commands and actual results: `.\.venv\Scripts\python.exe -m ruff check .` passed; `.\.venv\Scripts\python.exe -m ruff format --check .` passed; `.\.venv\Scripts\python.exe -m pytest -q` passed with `25 passed` and two dependency deprecation warnings. Earlier ruff check found one import-order issue and fixed it with `ruff check . --fix`.
- Design entry / related ADRs: docs/design.md Day 4 entry completed; ADR-001 accepted in docs/decisions.md.
- Untested assumptions: Request ID logging is tested through the test client but not observed from a live Uvicorn terminal session; no database-backed repository exists yet.
- Weak concepts: Keep reinforcing exception handlers versus route handlers for pre-handler validation failures.
- Optional work deferred: More advanced logging configuration and log shipping.
## Weekly gates
- [ ] Week 1: Durable validated CRUD
- [ ] Week 2: Isolated multi-user API
- [ ] Week 3: Recoverable background work
- [ ] Week 4: Operated release and capstone

## Blockers and deviations
- Git status could not be inspected because the folder is not a Git repository. Impact: no version-control diff evidence yet. Recovery action: initialize or connect Git when the learner wants repository tracking. Return point: Day 2 startup.
- The normal patch tool and some sandboxed commands failed because `codex-windows-sandbox-setup.exe` was unavailable. Recovery action: local workspace edits and validation were run with explicit escalation.

## Exact next session
- Module and phase: Day 5 / W1.5, Orient
- File/function/section: roadmap.md Day 5; proposed schema for users/workspaces/memberships/projects/tasks
- Next question or exercise: Draw the ER model and explain why constraints backstop API validation.
- Next build task: Add local PostgreSQL Compose configuration and initial relational schema/migration planning.
- Next validation command: `.\.venv\Scripts\python.exe -m pytest -q`









