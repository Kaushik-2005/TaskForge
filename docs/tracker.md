# Backend Learning Tracker

## Current position
- Roadmap: roadmap.md
- Day / module: Day 10 / W2.3 Transactions and concurrent writes
- Calendar date: 2026-09-13 to 2026-09-14
- Phase: Orient
- Status: In Progress
- Mode: Guided Learning
- Exact current task: Start Day 10 by learning lost updates, MVCC, row locks, optimistic concurrency, and transaction boundaries.
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
| 10 | W2.3 | 2026-09-14 | Not started | Not checked | In progress |
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
- Reading/sections: Day 10 uses BFP 08 transactions, BFP 20 races, and PostgreSQL transaction isolation documentation.
- Learner answer or concise evidence: Pending Day 10 transaction/concurrency explanation.
- Exercise path/result: Pending lost-update reproduction exercise.
- Changed files: Pending Day 10.
- Commands and actual results: Pending Day 10.
- Design entry / related ADRs: Pending Day 10 transaction/concurrency design entry.
- Untested assumptions: Need to prove concurrent task updates cannot silently overwrite each other. Legacy unauthenticated project/task routes still exist as a tracked limitation from Day 9.
- Weak concepts: Transactions do not automatically prevent every race; clarify lost updates and isolation levels.
- Optional work deferred: HTTP precondition headers are optional comparison; Day 10 can use version-based `409` if simpler.
## Weekly gates
- [x] Week 1: Durable validated CRUD
- [ ] Week 2: Isolated multi-user API
- [ ] Week 3: Recoverable background work
- [ ] Week 4: Operated release and capstone

## Blockers and deviations
- Git status could not be inspected because the folder is not a Git repository. Impact: no version-control diff evidence yet. Recovery action: initialize or connect Git when the learner wants repository tracking. Return point: Day 2 startup.
- The normal patch tool and some sandboxed commands failed because `codex-windows-sandbox-setup.exe` was unavailable. Recovery action: local workspace edits and validation were run with explicit escalation.

## Exact next session
- Module and phase: Day 10 / W2.3, Orient
- File/function/section: `src/taskforge/db_models.py`, `src/taskforge/repositories.py`, `src/taskforge/services.py`, `src/taskforge/api.py`, transaction/versioning design
- Next question or exercise: Explain how two concurrent task updates can create a lost update under read committed isolation.
- Next build task: Add version-based conditional task updates and audit events in one transaction.
- Next validation command: `.\.venv\Scripts\python.exe -m pytest -q tests\test_postgres_persistence.py` plus new concurrency tests


























