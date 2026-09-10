# Architecture Decisions

## ADR-001: Keep HTTP handlers separate from business services and storage
- Date and module: 2026-09-09, Day 4 / W1.4
- Status: Accepted
- Context / constraints: TaskForge started with route handlers calling an in-memory store directly. Day 4 introduces business rules, error mapping, and future worker/database entry points.
- Alternatives considered: Keep all logic in route handlers; put business rules in the store; introduce a service layer between HTTP and storage.
- Decision: Route handlers own HTTP parsing/response concerns, `TaskForgeService` owns business rules and application errors, and `InMemoryStore` owns temporary data access only.
- Reason: Business rules such as task status transitions should be reusable outside HTTP and testable without FastAPI. Storage should not know product behavior beyond mechanical persistence operations.
- Trade-offs and consequences: Adds a small amount of structure and more files early. In exchange, Day 5-6 database work and later worker/auth paths have a clearer boundary to plug into.
- Evidence: `tests/test_services.py` verifies the service rejects `todo -> done` while the store can mechanically update; HTTP tests still pass through the API boundary.
- Revisit trigger: Revisit if service methods become thin pass-throughs for several modules or if database repositories require a different application boundary.

## ADR-002: Use UUID-keyed relational schema with database-backed integrity constraints
- Date and module: 2026-09-10, Day 5 / W1.5
- Status: Accepted
- Context / constraints: TaskForge needs durable multi-user project/task data. API validation already exists, but durable data must remain valid across scripts, workers, migrations, tests, and future code paths.
- Alternatives considered: Trust only API validation; use natural/composite primary keys everywhere; use UUID surrogate primary keys plus natural unique constraints.
- Decision: Use UUID primary keys for users, workspaces, memberships, projects, and tasks. Enforce relationship and domain rules with foreign keys, unique constraints, NOT NULL, and CHECK constraints.
- Reason: UUID surrogate keys are easy to pass through APIs and reference from later tables. Database constraints make invalid durable states impossible even when application validation is bypassed or buggy.
- Trade-offs and consequences: UUIDs are wider than integer keys and less naturally ordered. A membership surrogate `id` means `(user_id, workspace_id)` still needs a unique constraint to prevent duplicate membership facts.
- Evidence: `tests/sql/constraints.sql` proves PostgreSQL rejects broken project/workspace references, duplicate memberships, and invalid task statuses. `tests/sql/queries.sql` proves authorized task lookup and zero-task project counts.
- Revisit trigger: Revisit if query plans later show UUID/index costs as a measured bottleneck or if membership rows need a composite primary key for a specific integration.

## ADR-003: Use request-scoped SQLAlchemy sessions for PostgreSQL persistence
- Date and module: 2026-09-10, Day 6 / W1.6
- Status: Accepted
- Context / constraints: TaskForge needs durable CRUD without allowing partial commits inside multi-step operations. The API is synchronous FastAPI code, and PostgreSQL is local through Compose.
- Alternatives considered: Keep memory storage as the runtime path; use one global SQLAlchemy session; let each repository method commit independently; create one request-scoped session and commit once at the boundary.
- Decision: The app owns the SQLAlchemy engine and finite connection pool. The FastAPI dependency creates one session per request, builds a service with a PostgreSQL repository, commits once after success, rolls back on exception, and closes the session. Repository methods may flush but do not commit.
- Reason: This preserves atomicity for multi-step service operations and prevents transaction/session state from leaking across requests.
- Trade-offs and consequences: Existing unit-style API tests must explicitly select the memory backend. Runtime startup now requires the database schema to be migrated before PostgreSQL-backed endpoints are used.
- Evidence: `tests/test_postgres_persistence.py` runs Alembic against isolated temporary PostgreSQL databases, verifies persisted data survives a new app instance, and verifies rollback removes uncommitted multi-step work.
- Revisit trigger: Revisit when async database access, explicit unit-of-work objects, or authenticated workspace scoping arrives.
