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
