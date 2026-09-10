# Backend Learning Tracker

## Current position
- Roadmap: roadmap.md
- Day / module: Day 5 / W1.5 Relational modeling and SQL
- Calendar date: 2026-09-10
- Phase: Review
- Status: Completed
- Mode: Guided Learning
- Exact current task: Day 5 core requirements completed; next action is to start Day 6 only when requested.
- Last updated: 2026-09-10

## Day-by-day progress
| Day | Module | Date(s) | Implementation | Understanding | Overall |
| --- | --- | --- | --- | --- | --- |
| 1 | W1.1 | 2026-09-09 | Completed | Checked | Completed |
| 2 | W1.2 | 2026-09-09 | Completed | Checked | Completed |
| 3 | W1.3 | 2026-09-09 | Completed | Checked | Completed |
| 4 | W1.4 | 2026-09-09 | Completed | Checked | Completed |
| 5 | W1.5 | 2026-09-10 | Completed | Checked | Completed |
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
- Reading/sections: Day 5 assigned readings were BFP 08 modeling, constraints, queries, transaction overview; PostgreSQL transaction isolation supplement. Covered primary keys, foreign keys, unique constraints, check constraints, joins, and why database constraints backstop API validation.
- Learner answer or concise evidence: Learner correctly explained that foreign keys enforce referential integrity in the database, unique memberships prevent ambiguous authorization, and proposed an ER model with users, workspaces, memberships, projects, and tasks including UUID primary keys, foreign keys, unique constraints, NOT NULL constraints, and role/status CHECK constraints. Learner wrote correct join queries for authorized tasks and project task counts after a comma syntax correction on the first SELECT list.
- Exercise path/result: ER model attempted and reviewed. SQL exercises completed: authorized task lookup through memberships/projects/tasks and per-project task counts using LEFT JOIN and COUNT(t.id). Relational model saved in docs/relational-model.md.
- Changed files: `README.md`, `compose.yaml`, `db/schema.sql`, `db/seed.sql`, `docs/decisions.md`, `docs/project-contract.md`, `docs/relational-model.md`, `docs/tracker.md`, `docs/learning.md`, `docs/design.md`, `docs/session-log.md`, `tests/sql/constraints.sql`, `tests/sql/queries.sql`.
- Commands and actual results: Docker 28.0.4 and Compose v2.34.0 available. First Postgres startup timed out, then port 5432 was unavailable; compose host port changed to 5433. `docker compose up -d postgres` succeeded. Container health became `healthy`. SQL files copied into container. `psql -f tests/sql/constraints.sql` passed and rolled back. `psql -f tests/sql/queries.sql` passed and rolled back. `.\.venv\Scripts\python.exe -m ruff check .` passed; `.\.venv\Scripts\python.exe -m ruff format --check .` passed; `.\.venv\Scripts\python.exe -m pytest -q` passed with `25 passed` and two dependency deprecation warnings.
- Design entry / related ADRs: docs/design.md Day 5 entry completed; ADR-002 accepted in docs/decisions.md.
- Untested assumptions: API does not use PostgreSQL yet; migration tooling/Alembic not introduced until Day 6; upgrade migration path not tested.
- Weak concepts: Continue reinforcing that API validation improves error quality, while database constraints protect durable truth.
- Optional work deferred: Composite membership primary key alternative; indexes beyond implicit PK/unique indexes; transaction anomaly labs for Day 10.
## Weekly gates
- [ ] Week 1: Durable validated CRUD
- [ ] Week 2: Isolated multi-user API
- [ ] Week 3: Recoverable background work
- [ ] Week 4: Operated release and capstone

## Blockers and deviations
- Git status could not be inspected because the folder is not a Git repository. Impact: no version-control diff evidence yet. Recovery action: initialize or connect Git when the learner wants repository tracking. Return point: Day 2 startup.
- The normal patch tool and some sandboxed commands failed because `codex-windows-sandbox-setup.exe` was unavailable. Recovery action: local workspace edits and validation were run with explicit escalation.

## Exact next session
- Module and phase: Day 6 / W1.6, Orient
- File/function/section: roadmap.md Day 6; `db/schema.sql`, `src/taskforge/store.py`, and future PostgreSQL repository boundary
- Next question or exercise: Explain request-scoped DB sessions, commit/rollback, and connection pool ownership.
- Next build task: Replace memory storage with PostgreSQL repositories using SQLAlchemy/psycopg and migration tooling.
- Next validation command: `.\.venv\Scripts\python.exe -m pytest -q`














