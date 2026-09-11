# Backend Learning Tracker

## Current position
- Roadmap: roadmap.md
- Day / module: Day 8 / W2.1 Authentication and sessions
- Calendar date: 2026-09-11
- Phase: Review
- Status: Completed
- Mode: Guided Learning
- Exact current task: Day 8 completed; next module is Day 9 authorization and tenant isolation.
- Last updated: 2026-09-11

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
- Reading/sections: Day 8 uses BFP 04 sessions/cookies/JWT/OAuth/OIDC plus OWASP session management and password storage guidance.
- Learner answer or concise evidence: Learner correctly explained authentication as proving the requester is a particular user, authorization as deciding allowed operations such as workspace/project access, and password hashing as one-way verification rather than reversible storage.
- Exercise path/result: Learner traced login success, expired `/me`, logout, and session theft correctly. Notes: local HTTP may need a documented non-Secure cookie exception; production HTTPS profile must use Secure cookies.
- Changed files: `src/taskforge/api.py`, `src/taskforge/auth_service.py`, `src/taskforge/auth_repository.py`, `src/taskforge/security.py`, `src/taskforge/errors.py`, `src/taskforge/models.py`, `src/taskforge/config.py`, `src/taskforge/db_models.py`, `migrations/versions/0002_add_sessions.py`, `tests/test_security.py`, `tests/test_auth_repository.py`, `tests/test_auth_api.py`, `tests/conftest.py`, docs and README.
- Commands and actual results: Initial migration test caught `sa.Columns` typo; corrected to `sa.Column`. `.\.venv\Scripts\python.exe -m pytest -q tests\test_security.py tests\test_auth_repository.py tests\test_auth_api.py` passed with `14 passed` and two dependency warnings. `.\.venv\Scripts\python.exe -m ruff check .` passed. `.\.venv\Scripts\python.exe -m pytest -q` passed with `48 passed` and two dependency warnings.
- Design entry / related ADRs: `docs/design.md` Day 8 entry updated. ADR-005 records opaque PostgreSQL-backed sessions.
- Untested assumptions: Project/task routes are not yet authorization-protected; Day 9 will bind operations to users, memberships, roles, and workspaces. Local HTTP uses a documented non-Secure-cookie exception.
- Weak concepts: Continue reinforcing that authentication proves identity but does not yet authorize project/task access.
- Optional work deferred: OAuth/OIDC remains comparison-only unless explicitly requested.
## Weekly gates
- [x] Week 1: Durable validated CRUD
- [ ] Week 2: Isolated multi-user API
- [ ] Week 3: Recoverable background work
- [ ] Week 4: Operated release and capstone

## Blockers and deviations
- Git status could not be inspected because the folder is not a Git repository. Impact: no version-control diff evidence yet. Recovery action: initialize or connect Git when the learner wants repository tracking. Return point: Day 2 startup.
- The normal patch tool and some sandboxed commands failed because `codex-windows-sandbox-setup.exe` was unavailable. Recovery action: local workspace edits and validation were run with explicit escalation.

## Exact next session
- Module and phase: Day 9 / W2.2, Orient
- File/function/section: roadmap.md Day 9; authorization, memberships, roles, and tenant-scoped repository paths
- Next question or exercise: Write an owner/admin/member/outsider permission matrix for workspaces, projects, and tasks.
- Next build task: Day 9 authorization: permission matrix, membership management, and tenant-scoped repository paths.
- Next validation command: `.\.venv\Scripts\python.exe -m pytest -q`



















