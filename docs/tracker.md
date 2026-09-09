# Backend Learning Tracker

## Current position
- Roadmap: roadmap.md
- Day / module: Day 1 / W1.1 Request journey and environment
- Calendar date: 2026-09-09
- Phase: Review
- Status: Completed
- Mode: Guided Learning
- Exact current task: Day 1 core requirements completed; next action is to start Day 2 only when requested.
- Last updated: 2026-09-09

## Day-by-day progress
| Day | Module | Date(s) | Implementation | Understanding | Overall |
| --- | --- | --- | --- | --- | --- |
| 1 | W1.1 | 2026-09-09 | Completed | Checked | Completed |
| 2 | W1.2 | - | Not started | Not checked | Not started |
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
- Reading/sections: Day 1 assigned readings were BFP 01 message anatomy, transport, TLS, methods, debugging; BFP 14 settings basics; RFC 9110 HTTP semantics. Covered selected request journey, local HTTP, and settings concepts in guided session.
- Learner answer or concise evidence: Learner correctly identified that a 404 from `/health/live` proves the server is reachable and HTTP routing was reached, while suggesting the endpoint path or registration is wrong. Learner explained HTTP statelessness and how cookies/tokens carry identity proof on later requests. Learner traced a successful curl request through address/port, TCP connection, GET path, route/handler, and 200 response.
- Exercise path/result: Verbal trace exercise completed and reviewed; missing response body detail was corrected.
- Changed files: `.gitignore`, `.env.example`, `pyproject.toml`, `README.md`, `src/taskforge/__init__.py`, `src/taskforge/config.py`, `src/taskforge/main.py`, `tests/test_health.py`, `docs/project-contract.md`, `docs/tracker.md`, `docs/learning.md`, `docs/session-log.md`, `docs/design.md`.
- Commands and actual results: `python --version` and `py --version` returned Python 3.12.0; `python -m venv .venv` succeeded; `.\.venv\Scripts\python.exe -m pip install -e ".[dev]"` succeeded; `.\.venv\Scripts\python.exe -m ruff check .` passed; `.\.venv\Scripts\python.exe -m ruff format --check .` passed after formatting; `.\.venv\Scripts\python.exe -m pytest -q` passed with `1 passed` and two dependency deprecation warnings; live Uvicorn smoke check returned `StatusCode=200` and body `{"status":"ok"}`.
- Design entry / related ADRs: docs/design.md Day 1 entry completed; no ADRs yet.
- Untested assumptions: No public deployment, TLS profile, readiness/dependency health, database behavior, or auth behavior exists yet.
- Weak concepts: None blocking for Day 1. Continue reinforcing that a health endpoint only proves a narrow request path.
- Optional work deferred: TLS/reverse proxy details beyond local explanation.

## Weekly gates
- [ ] Week 1: Durable validated CRUD
- [ ] Week 2: Isolated multi-user API
- [ ] Week 3: Recoverable background work
- [ ] Week 4: Operated release and capstone

## Blockers and deviations
- Git status could not be inspected because the folder is not a Git repository. Impact: no version-control diff evidence yet. Recovery action: initialize or connect Git when the learner wants repository tracking. Return point: Day 2 startup.
- The normal patch tool and some sandboxed commands failed because `codex-windows-sandbox-setup.exe` was unavailable. Recovery action: local workspace edits and validation were run with explicit escalation.

## Exact next session
- Module and phase: Day 2 / W1.2, Orient
- File/function/section: roadmap.md Day 2; existing `src/taskforge/main.py`
- Next question or exercise: Define resource routes and status codes for in-memory project/task CRUD.
- Next build task: Add `/api/v1` in-memory project/task CRUD with bounded list behavior and consistent errors.
- Next validation command: `.\.venv\Scripts\python.exe -m pytest -q`
