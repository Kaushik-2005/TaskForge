# Backend Learning Tracker

## Current position
- Roadmap: roadmap.md
- Day / module: Day 2 / W1.2 Routing and API contracts
- Calendar date: 2026-09-09
- Phase: Review
- Status: Completed
- Mode: Guided Learning
- Exact current task: Day 2 core requirements completed; next action is to start Day 3 only when requested.
- Last updated: 2026-09-09

## Day-by-day progress
| Day | Module | Date(s) | Implementation | Understanding | Overall |
| --- | --- | --- | --- | --- | --- |
| 1 | W1.1 | 2026-09-09 | Completed | Checked | Completed |
| 2 | W1.2 | 2026-09-09 | Completed | Checked | Completed |
| 3 | W1.3 | - | Not started | Not checked | Not started |
| 4 | W1.4 | - | Not started | Not checked | Not started |
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
- Reading/sections: Day 2 assigned readings were BFP 02; selected BFP 07 resource/method/status/pagination sections; RFC 9110 HTTP semantics. Covered selected route, resource, method, status, idempotency, and pagination concepts in guided session.
- Learner answer or concise evidence: Learner correctly chose `POST /api/v1/projects` over action-style GET for project creation, identified `201 Created`, and explained DELETE idempotency as same final server state even when repeated responses differ. Endpoint-table exercise was mostly correct; corrected task item route to plural `/tasks/{task_id}` and fixed brace typo.
- Exercise path/result: Endpoint table completed and reviewed; selected `PATCH` for partial updates.
- Changed files: `README.md`, `docs/project-contract.md`, `docs/tracker.md`, `docs/learning.md`, `docs/design.md`, `docs/session-log.md`, `src/taskforge/api.py`, `src/taskforge/main.py`, `src/taskforge/models.py`, `src/taskforge/store.py`, `tests/test_projects_tasks.py`.
- Commands and actual results: `.\.venv\Scripts\python.exe -m ruff check .` passed; `.\.venv\Scripts\python.exe -m ruff format --check .` passed; `.\.venv\Scripts\python.exe -m pytest -q` passed with `8 passed` and two dependency deprecation warnings. Earlier test run failed because Starlette-generated 405 responses were not caught by the FastAPI HTTPException handler; fixed by handling StarletteHTTPException.
- Design entry / related ADRs: docs/design.md Day 2 entry completed; no ADRs yet.
- Untested assumptions: Data is process-local memory only; no persistence, auth, tenant isolation, concurrent write behavior, or database constraints exist yet.
- Weak concepts: Continue reinforcing the difference between route shape, method semantics, and persistence behavior.
- Optional work deferred: Deep version migration strategy beyond reserving `/api/v1`.
## Weekly gates
- [ ] Week 1: Durable validated CRUD
- [ ] Week 2: Isolated multi-user API
- [ ] Week 3: Recoverable background work
- [ ] Week 4: Operated release and capstone

## Blockers and deviations
- Git status could not be inspected because the folder is not a Git repository. Impact: no version-control diff evidence yet. Recovery action: initialize or connect Git when the learner wants repository tracking. Return point: Day 2 startup.
- The normal patch tool and some sandboxed commands failed because `codex-windows-sandbox-setup.exe` was unavailable. Recovery action: local workspace edits and validation were run with explicit escalation.

## Exact next session
- Module and phase: Day 3 / W1.3, Orient
- File/function/section: roadmap.md Day 3; existing `src/taskforge/models.py` and API request/response bodies
- Next question or exercise: Classify malformed JSON, invalid IDs, oversized fields, forbidden state changes, and unexpected fields by rejection layer.
- Next build task: Separate create/update/read models more strictly, add payload limits and explicit patch semantics.
- Next validation command: `.\.venv\Scripts\python.exe -m pytest -q`



