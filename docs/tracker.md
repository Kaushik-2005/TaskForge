# Backend Learning Tracker

## Current position
- Roadmap: roadmap.md
- Day / module: Day 3 / W1.3 Serialization and validation
- Calendar date: 2026-09-09
- Phase: Review
- Status: Completed
- Mode: Guided Learning
- Exact current task: Day 3 core requirements completed; next action is to start Day 4 only when requested.
- Last updated: 2026-09-09

## Day-by-day progress
| Day | Module | Date(s) | Implementation | Understanding | Overall |
| --- | --- | --- | --- | --- | --- |
| 1 | W1.1 | 2026-09-09 | Completed | Checked | Completed |
| 2 | W1.2 | 2026-09-09 | Completed | Checked | Completed |
| 3 | W1.3 | 2026-09-09 | Completed | Checked | Completed |
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
- Reading/sections: Day 3 assigned readings were BFP 03 serialization/deserialization and BFP 05 validation/transformation sections. Covered parsing, schema validation, contract validation, domain validation, missing/null PATCH behavior, UUID path parsing, and response boundaries.
- Learner answer or concise evidence: Learner correctly classified malformed JSON as JSON parsing, empty name as schema validation, unexpected `is_admin` field as contract validation, and forbidden task status jump as domain validation.
- Exercise path/result: Classification exercise completed and reviewed. Validation tests added for malformed JSON, unknown fields, null/missing PATCH behavior including explicit null task title, status transition conflicts, invalid UUIDs, and response field boundaries.
- Changed files: `README.md`, `docs/project-contract.md`, `docs/tracker.md`, `docs/learning.md`, `docs/design.md`, `docs/session-log.md`, `src/taskforge/api.py`, `src/taskforge/models.py`, `src/taskforge/store.py`, `tests/test_projects_tasks.py`, `tests/test_validation.py`.
- Commands and actual results: Initial Day 3 validation tests failed for unknown fields, status transition, and invalid UUID handling; a later explicit-null test exposed that raw `ValueError` objects in validation details needed JSON-safe encoding; after implementation, `.\.venv\Scripts\python.exe -m ruff check .` passed; `.\.venv\Scripts\python.exe -m ruff format --check .` passed; `.\.venv\Scripts\python.exe -m pytest -q` passed with `18 passed` and two dependency deprecation warnings.
- Design entry / related ADRs: docs/design.md Day 3 entry completed; no ADRs yet.
- Untested assumptions: No global body-size limit middleware yet; no auth-sensitive response fields exist yet; no persistence constraints exist yet.
- Weak concepts: Continue reinforcing malformed-ID `422` versus valid-missing-ID `404`.
- Optional work deferred: Full payload byte-size limits beyond field length validation.
## Weekly gates
- [ ] Week 1: Durable validated CRUD
- [ ] Week 2: Isolated multi-user API
- [ ] Week 3: Recoverable background work
- [ ] Week 4: Operated release and capstone

## Blockers and deviations
- Git status could not be inspected because the folder is not a Git repository. Impact: no version-control diff evidence yet. Recovery action: initialize or connect Git when the learner wants repository tracking. Return point: Day 2 startup.
- The normal patch tool and some sandboxed commands failed because `codex-windows-sandbox-setup.exe` was unavailable. Recovery action: local workspace edits and validation were run with explicit escalation.

## Exact next session
- Module and phase: Day 4 / W1.4, Orient
- File/function/section: roadmap.md Day 4; route handlers in `src/taskforge/api.py` and storage logic in `src/taskforge/store.py`
- Next question or exercise: Trace a task update through handler, service, repository/store, and error mapping boundaries.
- Next build task: Split HTTP handlers from service rules, add request IDs, structured logs, startup config validation, and service tests.
- Next validation command: `.\.venv\Scripts\python.exe -m pytest -q`







