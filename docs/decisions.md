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

## ADR-004: Treat PostgreSQL as the Week 1 runtime source of truth
- Date and module: 2026-09-11, Day 7 / W1.7
- Status: Accepted
- Context / constraints: Week 1 started with memory-backed CRUD for learning speed, then introduced PostgreSQL schema, migrations, repositories, and integration tests. Day 7 reviewed whether the foundation is ready for authentication and authorization work.
- Alternatives considered: Keep both memory and PostgreSQL as equal runtime backends; remove memory storage entirely; use PostgreSQL as the default runtime backend while keeping memory storage only for focused tests.
- Decision: PostgreSQL is the runtime source of truth for local development. Memory storage remains only as a focused test backend for HTTP/service contract tests where database behavior is not under test.
- Reason: Week 2 identity and authorization work need durable relational state. Keeping memory as a production-like path would hide transaction, migration, and multi-process persistence concerns.
- Trade-offs and consequences: Tests must be explicit about whether they exercise memory contract behavior or real PostgreSQL behavior. Runtime setup requires PostgreSQL and Alembic migration before using the default backend.
- Evidence: Day 7 fresh-start rehearsal in `C:\tmp\taskforge-fresh-20260911` created a new venv, installed dependencies, and passed ruff, format check, and pytest. Manual Day 6 testing verified data persisted across Uvicorn restart.
- Revisit trigger: Revisit if a later test strategy removes the memory store entirely or if a different persistence backend is introduced.

## ADR-005: Use opaque PostgreSQL-backed sessions for authentication
- Date and module: 2026-09-11, Day 8 / W2.1
- Status: Accepted
- Context / constraints: TaskForge needs login, logout, expiry, revocation, and later authorization. Local development uses FastAPI with PostgreSQL already configured as the source of truth.
- Alternatives considered: Store user identity directly in a signed cookie or JWT; use opaque random session IDs stored in PostgreSQL; defer sessions until authorization.
- Decision: Use high-entropy opaque session tokens in an HttpOnly cookie. Store only hashed session tokens and hashed CSRF tokens in PostgreSQL with expiry and revocation timestamps.
- Reason: Server-side sessions make logout and forced revocation straightforward and keep authorization state out of client-controlled tokens. Hashing stored tokens limits damage if the sessions table leaks.
- Trade-offs and consequences: Every authenticated request needs a database lookup until caching is deliberately introduced. Local HTTP uses a documented non-Secure-cookie exception; production HTTPS must enable Secure cookies. CSRF protection is required because browsers attach cookies automatically.
- Evidence: Day 8 tests cover wrong credentials, `/me`, expired sessions, logout revocation, new token issuance on login, CSRF rejection/acceptance, and Secure cookie configuration.
- Revisit trigger: Revisit if TaskForge integrates an external identity provider, needs stateless edge verification, or adds a cache with a documented session freshness/revocation policy.

## ADR-006: Enforce tenant-scoped object authorization in repository lookups
- Date and module: 2026-09-14, Day 9 / W2.2
- Status: Accepted
- Context / constraints: Authenticated users can belong to different workspaces. Project and task IDs are guessable enough that every object lookup must prove the current user has membership in the object's workspace.
- Alternatives considered: Fetch objects by ID first and then check membership; return `403` for every unauthorized object; use tenant-scoped SQL lookups that return no row outside the user's workspace boundary.
- Decision: Workspace-scoped project and task lookups join or check memberships as part of the repository path. Task lookups also verify the supplied parent project. Membership mutations verify the actor role and preserve at least one owner. Cross-tenant, wrong-parent, or nonexistent objects return `404`. In-tenant role denials, such as a member deleting a project, return `403`.
- Reason: Returning `404` outside the tenant boundary avoids leaking object existence. Returning `403` inside the tenant boundary gives a legitimate workspace member an accurate permission failure.
- Trade-offs and consequences: Repository methods need explicit user/workspace/object parameters instead of generic `get_project(project_id)` calls. Tests must cover outsider invisibility and same-tenant role denial separately.
- Evidence: `tests/test_authorization.py` covers owner project and task read/update/delete, outsider `404` for project/task access, member `403` for project delete, membership add/list/update/delete role behavior, duplicate membership `409`, last-owner `409`, and foreign task under own project returning `404`. Full pytest passed with 75 tests.
- Revisit trigger: Revisit when membership-management endpoints, task authorization, or a dedicated policy abstraction is introduced.


