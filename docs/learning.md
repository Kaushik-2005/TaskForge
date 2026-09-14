# Backend Systems Learning Notes

## Week 1

### Day 1 - W1.1: Request journey and environment

#### Concept and why it exists
An HTTP request is a structured message sent by a client to a server process. The request journey matters because many backend failures happen before application code runs: the address may not resolve, the port may not accept connections, TLS may fail, a proxy may reject the request, or the application may not route it correctly.

A health endpoint exists to prove a narrow fact: the API process can receive a request and return a response from application code. It is not proof that deeper dependencies such as databases, auth, or job workers are healthy.

#### Mental model and small example
For local Day 1 work, the request path is:

```text
client command -> localhost address -> TCP connection -> HTTP request bytes -> API router -> handler -> HTTP response
```

Example command:

```powershell
curl -i http://127.0.0.1:8000/health/live
```

Expected response shape:

```http
HTTP/1.1 200 OK
content-type: application/json

{"status":"ok"}
```

#### What happens internally
The client resolves the target address, opens a TCP connection to an IP address and port, writes an HTTP request line and headers, then waits for response bytes. A local Uvicorn server accepts the connection, parses the HTTP message, passes it into FastAPI/Starlette routing, matches `GET /health/live`, calls the handler, serializes the returned dictionary as JSON, and writes an HTTP response.

#### Boundaries, failure modes, and common mistakes
- Name/address failure: the client cannot resolve or reach the address.
- Connection failure: no process is listening, the wrong port is used, or traffic is blocked.
- HTTP parsing/routing failure: the server is reachable, but method/path does not match an endpoint.
- Application failure: the route exists, but handler code raises or returns the wrong contract.
- Common mistake: saying "the API is down" without distinguishing network reachability, HTTP routing, and handler behavior.

A `404` from `/health/live` proves the server returned an HTTP response and routing was reached, but it does not prove the final endpoint handler ran. It usually suggests a wrong path, missing route registration, wrong app instance, or unexpected route prefix.

#### Alternatives and trade-offs
Local development uses plain HTTP on `127.0.0.1` because it is easy to inspect and does not cross an untrusted network. Production should use TLS at a trusted boundary, often a reverse proxy or load balancer, because credentials and cookies must not be sent over untrusted networks in clear text.

HTTP is stateless at the protocol level: each request must carry what the server needs to process it. TaskForge can still support login sessions later by sending a session cookie on each protected request and validating that session ID against server-side state.

#### TaskForge application
Day 1 added a minimal FastAPI app:

- `src/taskforge/config.py`: settings object loaded from environment variables with `TASKFORGE_` prefix.
- `src/taskforge/main.py`: FastAPI application factory and `GET /health/live` route.
- `tests/test_health.py`: smoke test using FastAPI's test client.
- `.env.example`: non-secret example local configuration.

#### Exercise and validation observations
Learner traced a successful `curl -i http://127.0.0.1:8000/health/live` through address/port, TCP connection, HTTP GET path, route/handler, and success status. Correction: include the response body as part of the observable contract.

Validation results on 2026-09-09:

- `.\.venv\Scripts\python.exe -m ruff check .`: passed.
- `.\.venv\Scripts\python.exe -m ruff format --check .`: passed after formatting three Python files.
- `.\.venv\Scripts\python.exe -m pytest -q`: `1 passed`, with two dependency deprecation warnings from FastAPI/Starlette test client internals.
- Runtime smoke check against Uvicorn: `StatusCode=200`, body `{"status":"ok"}`.

#### Interview explanation
A good concise explanation: "A local health request connects to `127.0.0.1` on the server port, sends an HTTP GET for `/health/live`, and the server routes it to a FastAPI handler that returns `200 {"status":"ok"}`. If the connection fails, the server may not be listening. If the response is 404, the server is reachable but route matching failed. If the route returns 500, the request likely reached application code and the handler failed. HTTP itself does not remember users, but later TaskForge can maintain login continuity by requiring each request to carry a cookie containing a session ID that the server validates."

#### Sources: links, sections, required/optional
- Required: BFP 01 HTTP & CORS, selected sections on message anatomy, transport, TLS, methods, and debugging.
- Required: BFP 14 Configuration Management, settings basics.
- Required: RFC 9110 HTTP Semantics.

#### My questions, corrections, and revision items
- Reinforce that a 404 proves server reachability but not handler execution.
- Reinforce that health endpoints prove a narrow capability, not full system readiness.

### Day 2 - W1.2: Routing and API contracts

#### Concept and why it exists
Routing maps an HTTP method and path to application behavior. API contracts matter because clients need stable promises: which resource a path identifies, which methods are allowed, what status codes mean, and what shape success and error bodies have.

#### Mental model and small example
A resource-oriented route names the thing, while the HTTP method gives the action semantics:

```http
POST /api/v1/projects
GET /api/v1/projects/{project_id}
DELETE /api/v1/projects/{project_id}
```

Prefer `POST /api/v1/projects` over `GET /api/v1/create-project` because creating changes server state and `projects` is the resource collection.

#### What happens internally
FastAPI matches the incoming method and path template, parses path and query parameters, validates request bodies when models exist, then calls the registered handler. If no route matches the path, the client gets 404. If the path matches but the method is not allowed, the client gets 405.

#### Boundaries, failure modes, and common mistakes
- `GET` should be safe: do not create/update/delete state from a GET route.
- `POST` to a collection usually creates a new resource and often returns `201 Created` plus `Location`.
- Idempotent means repeated calls have the same intended final server state; it does not require identical responses.
- `DELETE /api/v1/projects/123` may return `204` first and then either `204` or `404` on repeat, depending on the contract, while still being idempotent.
- Common mistake: putting verbs in paths, such as `/create-project`, instead of modeling resources and using method semantics.

#### Alternatives and trade-offs
Resource-style REST paths make contracts easier to test and document as the API grows. Action-style RPC paths can be useful for operations that do not map cleanly to resources, but basic CRUD should start with resource collections and resource identifiers.

#### TaskForge application
Day 2 added in-memory project/task CRUD under `/api/v1`:

- `src/taskforge/api.py`: resource routes, page-size bounds, status codes, and `Location` headers.
- `src/taskforge/models.py`: initial Pydantic request and response models.
- `src/taskforge/store.py`: process-local in-memory project/task storage.
- `src/taskforge/main.py`: route inclusion and JSON error-envelope handlers.
- `tests/test_projects_tasks.py`: HTTP contract tests for CRUD, missing resources, wrong method, pagination bounds, and OpenAPI route presence.

Tasks are nested under projects because a task is not currently a top-level resource in the API contract. The corrected item route is plural and consistent: `/api/v1/projects/{project_id}/tasks/{task_id}`.

#### Exercise and validation observations
Learner endpoint table was mostly correct. Corrections:

- Use `/tasks/{task_id}` consistently, not singular `/task/{task_id}`.
- Close path parameters with `}`.
- `201 Created` should include a `Location` header for newly created resources.
- FastAPI validation failures use `422` in this implementation; malformed or out-of-bounds input is wrapped in the project error envelope.

Validation results on 2026-09-09:

- `.\.venv\Scripts\python.exe -m ruff check .`: passed.
- `.\.venv\Scripts\python.exe -m ruff format --check .`: passed.
- `.\.venv\Scripts\python.exe -m pytest -q`: `8 passed`, with two dependency deprecation warnings from FastAPI/Starlette test client internals.

A useful failure occurred before the final pass: a custom Pydantic validator placed a raw `ValueError` object inside validation details, which the JSON response could not serialize. The handler now runs validation details through FastAPI's `jsonable_encoder`.

#### Interview explanation
A good concise explanation: "TaskForge models projects and nested tasks as resources under `/api/v1`. Creating a project uses `POST /api/v1/projects` because creation changes server state and the server assigns the new ID. A successful create returns `201 Created` and a `Location` header. Reading uses `GET`, deletion uses `DELETE`, and partial changes use `PATCH`. DELETE can still be idempotent even if a repeated call returns a different status, because idempotency is about the final intended server state. List endpoints bound `page_size` to protect the API from unbounded responses."

#### Sources: links, sections, required/optional
- Required: BFP 02 Routing in Backend.
- Required: BFP 07 selected REST design sections on resources, methods, status codes, and pagination.
- Required: RFC 9110 HTTP Semantics.

#### My questions, corrections, and revision items
- Learner correctly explained POST versus GET for creation.
- Learner identified `201 Created`; add `Location` header as the resource URI.
- Learner correctly explained DELETE idempotency as final-state semantics, not identical responses.



### Day 3 - W1.3: Serialization and validation

#### Concept and why it exists
Serialization turns in-memory objects into response bytes. Deserialization turns request bytes into data structures. Validation decides whether the parsed data is acceptable for the API contract and business rules.

Parsing valid JSON is only the first step. A request can be syntactically valid JSON but still fail because a field is empty, an enum value is unsupported, an unknown field is present, or the requested business transition is forbidden.

#### Mental model and small example
```text
raw HTTP body -> JSON parsing -> schema validation -> contract validation -> domain validation -> handler/store -> response serialization
```

Examples:

- `{name: "Launch plan"}` fails JSON parsing because object keys must be quoted.
- `{"name":""}` fails schema validation because the name is too short.
- `{"name":"Launch plan","is_admin":true}` should fail contract validation if unknown fields are forbidden.
- A task status jump from `todo` directly to `done` is a domain validation problem if the API contract says that transition is not allowed.

#### What happens internally
FastAPI reads the request body, asks the JSON parser to decode it, then uses Pydantic models and parameter annotations to validate shape and types. Route code should handle business rules that need current object state, such as a task's existing status.

#### Boundaries, failure modes, and common mistakes
- Malformed JSON is not a business-rule problem; the body cannot be decoded.
- Schema validation handles field types, lengths, enum values, and required fields.
- Contract validation decides whether extra client fields are allowed or rejected.
- Domain validation uses application state or business rules, such as allowed task status transitions.
- Response models prevent accidental output shape drift and later help avoid leaking sensitive fields.

#### Alternatives and trade-offs
Strict contracts reject unknown fields early and catch client mistakes, but they make clients update when the contract changes. Permissive contracts can be easier during prototyping, but clients may believe ignored fields were honored. TaskForge will prefer explicit accepted fields for learning and safety.

#### TaskForge application
Day 3 tightened the API boundary:

- Unknown fields are rejected with Pydantic `extra="forbid"` on request models.
- Path IDs are parsed as UUIDs, so malformed IDs fail before store lookup.
- PATCH distinguishes missing from null: omitted task fields are left unchanged; null values are not accepted for non-nullable project names.
- Empty task PATCH bodies are rejected because they request no change.
- Explicit `null` task titles are rejected even when another field is updated; an omitted title is left unchanged.
- Task status cannot move directly from `todo` to `done`; that is a domain validation rule enforced by the store for now and mapped to `409` by the route.
- Response models keep output fields explicit.

#### Exercise and validation observations
Learner correctly classified malformed JSON, empty name, unexpected `is_admin`, and forbidden task transition by rejection layer.

#### Interview explanation
A good concise explanation: "TaskForge separates parsing, schema validation, contract validation, and domain validation. Malformed JSON fails before the request model exists. Empty strings, invalid enum values, out-of-bounds page sizes, and malformed UUID path parameters fail schema validation. Unknown request fields fail contract validation because the API does not silently ignore fields like `is_admin`. A task status jump from `todo` directly to `done` is domain validation because it depends on the current task state. Response models define what the API sends back, which prevents accidental output shape drift."

#### Sources: links, sections, required/optional
- Required: BFP 03 serialization/deserialization.
- Required: BFP 05 validation and transformations.

#### My questions, corrections, and revision items
- Learner correctly classified Day 3 rejection layers.
- Important correction: invalid UUID path shape returns `422`, while a valid UUID that is not in storage returns `404`.
- Full payload byte-size limits are still deferred; current checks cover field length and page-size bounds.



### Day 4 - W1.4: Layers and configuration

#### Concept and why it exists
Layering keeps different kinds of decisions in the right place. HTTP route handlers should not become the whole application; they should translate HTTP requests into application calls and translate application results back into HTTP responses.

#### Mental model and small example
```text
HTTP route -> service -> store/repository -> service result/error -> HTTP response
```

For task update: the route parses UUIDs and request body, the service checks business rules, the store loads/saves data, and exception handlers format expected failures.

#### What happens internally
FastAPI handles routing and validation before route logic runs. The route calls a service with already-parsed values. The service asks the store for data and decides whether business rules allow the operation. Errors are raised as application exceptions and mapped to public HTTP errors at the API boundary.

#### Boundaries, failure modes, and common mistakes
- Business rules belong in services, not route handlers or storage code.
- Validation errors can happen before route handlers run, so public validation formatting belongs in exception handlers.
- Middleware is for cross-cutting request behavior such as request IDs, timing, and logging.
- Configuration should fail at startup when required values are invalid, not later during a request.

#### Alternatives and trade-offs
Small apps can start route-heavy, but business rules become harder to reuse and test. A service layer adds a little structure now and pays off as database persistence, workers, and authorization arrive.

#### TaskForge application
Day 4 introduced clearer application boundaries:

- `src/taskforge/api.py`: HTTP route handlers and service-error-to-HTTP mapping.
- `src/taskforge/services.py`: business rules and application-level missing-resource errors.
- `src/taskforge/store.py`: process-local data access only.
- `src/taskforge/errors.py`: application exception types.
- `src/taskforge/main.py`: app construction, request ID middleware, JSON access logs, validation/HTTP exception handlers, and startup settings load.
- `src/taskforge/config.py`: startup settings validation for environment and log level.

The `todo -> done` task transition rule moved out of storage and into `TaskForgeService`.

#### Exercise and validation observations
Learner correctly placed the status-transition rule in the service layer and corrected the validation error-envelope boundary after seeing that invalid UUIDs fail before handler execution.

Learner traced a forbidden task update:

- Route parses UUIDs and request body, then calls the service.
- Service fetches current state and rejects `todo -> done`.
- Store mutates only when the service approves.
- API boundary maps the domain error to `409 Conflict`.

Validation results on 2026-09-09:

- `.\.venv\Scripts\python.exe -m ruff check .`: passed.
- `.\.venv\Scripts\python.exe -m ruff format --check .`: passed.
- `.\.venv\Scripts\python.exe -m pytest -q`: `25 passed`, with two dependency deprecation warnings.

#### Interview explanation
A good concise explanation: "TaskForge now separates HTTP, application, and storage responsibilities. Routes parse valid requests and map service results to HTTP responses. The service owns business rules like task status transitions and raises application errors. The store only performs temporary in-memory data access. Validation errors can happen before route handlers run, so exception handlers own public error envelopes. Middleware owns request IDs and structured access logs because those apply to every request. Startup settings are validated before the app serves traffic."

#### Sources: links, sections, required/optional
- Required: BFP 06 controllers, services, and middleware.
- Required: BFP 14 settings basics and startup validation.
- Required: BFP 12 error classification.

#### My questions, corrections, and revision items
- Reinforce exception handler ownership for validation failures that occur before route handlers run.
- ADR-001 records the route/service/store boundary decision.


### Day 5 - W1.5: Relational modeling and SQL

#### Concept and why it exists
Relational modeling defines the durable shape of the system: entities, relationships, and invariants. API validation catches bad requests early, but database constraints protect the source of truth from every write path.

#### Mental model and small example
```text
users -> memberships -> workspaces -> projects -> tasks
```

A foreign key says a child row cannot point at a missing parent row. A unique constraint prevents duplicate facts. A check constraint keeps a column inside an allowed domain.

#### What happens internally
PostgreSQL validates constraints during writes. If an insert or update would violate a foreign key, unique constraint, not-null rule, or check constraint, the database rejects the write even if application code forgot to validate it.

#### Boundaries, failure modes, and common mistakes
- Do not rely only on API validation for durable data integrity.
- Foreign keys prevent orphaned rows.
- `UNIQUE (user_id, workspace_id)` prevents ambiguous memberships.
- `CHECK` constraints protect finite states such as roles and task statuses.
- Common mistake: modeling a relationship in code but not enforcing it in the database.

#### Alternatives and trade-offs
A surrogate `id` on memberships can make references and audit trails easier, but `UNIQUE (user_id, workspace_id)` is still needed because the real-world fact should occur only once. Composite primary keys are also possible, but can become cumbersome when other tables need to reference a membership.

#### TaskForge application
Learner proposed users, workspaces, memberships, projects, and tasks with UUID primary keys, foreign keys, uniqueness, NOT NULL, and role/status checks. Correction: `password_hash` column name should be spelled consistently.

#### Exercise and validation observations
Learner correctly explained database referential integrity and membership uniqueness. Learner wrote an authorized task query joining memberships -> projects -> tasks, with a correction for missing SELECT commas. Learner wrote a correct project-count query using LEFT JOIN so projects with zero tasks are included.

#### Interview explanation
A good concise explanation: "TaskForge uses relational constraints because durable data must remain valid even outside the current API path. Foreign keys prevent orphaned projects and tasks. `UNIQUE (user_id, workspace_id)` prevents ambiguous memberships. CHECK constraints keep roles and task statuses inside allowed sets. The authorized task query joins memberships to projects to tasks so access is proven through workspace membership. A LEFT JOIN with `COUNT(t.id)` includes projects that have zero tasks."

#### Sources: links, sections, required/optional
- Required: BFP 08 modeling, constraints, queries, transaction overview.
- Required supplement: PostgreSQL transaction isolation.

#### My questions, corrections, and revision items
- Decide whether tasks should include `workspace_id` directly or derive workspace ownership through project joins.
- Practice joins for authorized task lookup and per-project task counts. Day 5 SQL scripts passed against local PostgreSQL on host port 5433.



### Day 6 - W1.6: Persistence and migrations
#### Concept and why it exists
A durable API cannot keep project and task data only in process memory. PostgreSQL must become the authoritative store, and each request must use a controlled unit of work so related writes are atomic.

#### Mental model and small example
A request borrows database access for a short time, performs repository operations through the service, then commits once if the whole operation succeeds. If any required step fails, the transaction rolls back so no partial state remains.

#### What happens internally
A connection pool owns a finite number of reusable database connections. A request-scoped SQLAlchemy session uses a connection when it needs to run SQL and participates in a transaction. Repository methods should normally `add` or `flush` changes, not commit independently. The transaction boundary commits or rolls back and returns the connection to the pool.

#### Boundaries, failure modes, and common mistakes
A common mistake is committing inside each repository method. That can leave partial durable state when a later step in the same logical operation fails. Another mistake is using one global session across requests, which can leak transaction state and is unsafe under concurrency.

#### TaskForge application
Day 6 will keep the service as the business-rule boundary while replacing process-local storage with PostgreSQL-backed repositories. Migrations must run separately from requests, and integration tests must use isolated PostgreSQL state rather than developer data.

#### Exercise and validation observations
Learner correctly identified the partial-state failure from per-repository commits: project committed, first default task committed, second task fails, and later rollback cannot undo earlier commits. Learner also correctly explained that `flush()` sends SQL within the current transaction while `commit()` permanently completes the transaction.

#### Interview explanation
For a multi-step business operation, repositories should not independently commit. They should write or flush inside the current transaction. The request/session boundary commits once after the service operation succeeds or rolls back if any required step fails, preserving atomicity.

#### Sources: links, sections, required/optional
Roadmap Day 6: BFP 08 database access; BFP 22 integration tests/fixtures.

#### My questions, corrections, and revision items
Learner correctly identified that a project plus default tasks created in one logical operation should commit once after all steps succeed, with rollback on failure. Learner correctly explained total connection pool demand across processes: each worker has an independent pool, so maximum demand is `(pool_size + max_overflow) * worker_processes`; for 4 workers with pool size 5 and overflow 2, that is 28 connections.

### Day 7 - W1.7: Foundation review
#### Concept and why it exists
Week 1 review verifies that TaskForge's request, validation, service, persistence, migration, and testing boundaries are understood together rather than as isolated code changes.

#### Exercise and validation observations
Learner correctly explained the PostgreSQL-backed project creation path, separation between route/service/repository responsibilities, parsing/schema/domain failure categories, why migrations do not run during requests, and why tests use isolated temporary databases. Learner debugged the `COUNT(*)` with `LEFT JOIN` issue: zero-task projects can be counted as one preserved joined row, so the corrected aggregate is `COUNT(t.id)` with explicit grouping. Learner implemented `name_contains` project filtering through route, service, memory store, PostgreSQL repository, and tests.

#### My questions, corrections, and revision items
Continue reinforcing that migrations are deployment/admin operations and request handlers should assume the schema already exists. Day 7 fresh-start rehearsal proved the setup path in a clean copy under `C:\tmp\taskforge-fresh-20260911`: venv creation, dependency install, ruff, format check, and pytest all passed. Week 1 gate completed with PostgreSQL as runtime source of truth and memory storage retained only for focused tests.

### Day 8 - W2.1: Authentication and sessions
#### Concept and why it exists
Authentication proves who is making a request. Authorization decides what that authenticated user may do. TaskForge needs both because later workspace isolation depends on knowing the user first, then checking membership and role.

#### Mental model and small example
A login request verifies an email and password, creates a server-side session, sends an opaque session ID in a cookie, and later requests present that cookie. The server looks up the session to identify the current user.

#### What happens internally
Passwords are stored as password hashes, not plaintext and not reversible encrypted values. Login verifies a submitted password against the stored hash. Session IDs should be unpredictable opaque secrets; the database stores session state such as user ID, expiry, revocation, and rotation metadata.

#### Boundaries, failure modes, and common mistakes
A common mistake is confusing authentication with authorization. Another is storing recoverable passwords or placing user data directly in a cookie without server-side revocation. Cookie-authenticated unsafe requests also need CSRF protection.

#### TaskForge application
Day 8 introduced registration/login/logout/me, maintained password hashing, server-side sessions, cookie behavior, expiry/revocation, and CSRF protection for cookie-authenticated mutations.

#### Exercise and validation observations
Learner correctly traced login success, expired `/me`, logout, and stolen session behavior. Expired sessions should not return user data and may be invalidated. Logout invalidates/deletes server-side session state and clears the browser cookie. A stolen session can impersonate the user until expiry/revocation, limited by expiration, revocation, secure random IDs, HttpOnly/SameSite/Secure cookie policy, CSRF protection, and authorization checks. Local plain HTTP requires a documented exception for Secure cookies; production HTTPS must use Secure cookies.

#### My questions, corrections, and revision items
Learner correctly explained authentication versus authorization and why password hashes are used instead of encryption. Learner added `SessionRow` and a sessions migration; the migration test caught a typo (`sa.Columns` instead of `sa.Column`), proving the migration file executes against an empty PostgreSQL database. Learner added password hashing and token hashing helpers. Passwords use `pwdlib` recommended hashing; server-generated session/CSRF tokens use SHA-256 hashes plus constant-time comparison because the raw tokens are high-entropy random secrets. Learner added `AuthRepository` with user creation/email lookup, session creation, session revocation, and active-session lookup. Repository tests cover active, expired, revoked, and missing-session behavior against migrated PostgreSQL databases. The final API exposes `/api/v1/auth/register`, `/api/v1/auth/login`, `/api/v1/auth/logout`, and `/api/v1/auth/me`. Login issues a fresh opaque session cookie and returns a CSRF token; only token hashes are stored. Expired and revoked sessions return `401 unauthenticated`. Cookie-authenticated unsafe project/task mutations require `X-CSRF-Token`. Local HTTP uses a documented non-Secure-cookie exception; the HTTPS release profile can set Secure cookies.


#### Interview explanation
TaskForge uses opaque server-side sessions instead of self-contained JWTs for the first auth implementation. On registration, the password is hashed with a maintained password hashing library before storage. On login, the service normalizes the email, verifies the submitted password against the stored hash, creates fresh high-entropy session and CSRF tokens, stores only their hashes in PostgreSQL, and sends the raw session token in an HttpOnly SameSite=Lax cookie. `/me` looks up a valid, unexpired, unrevoked session. Logout revokes the server-side session and clears the browser cookie. Because browsers attach cookies automatically, unsafe cookie-authenticated mutations require the matching CSRF token in `X-CSRF-Token`.

### Day 9 - W2.2: Authorization and tenant isolation
#### Concept and why it exists
Authorization decides what an authenticated user may do. TaskForge must enforce membership and role checks on every workspace, project, and task data path so one tenant cannot read or mutate another tenant's data.

#### Mental model and small example
Authentication answers: who is this requester? Authorization answers: can this requester perform this operation on this object?

For object-level access, the lookup must prove both the object relationship and the user's membership:

```sql
SELECT p.*
FROM projects p
JOIN memberships m
  ON m.workspace_id = p.workspace_id
WHERE p.id = :project_id
  AND m.user_id = :current_user_id;
```

If no row is returned, the project is either absent or outside the user's tenant boundary.

#### Boundaries, failure modes, and common mistakes
Outside the user's accessible tenant boundary should behave as not found so object existence is not leaked across tenants. Inside the user's accessible workspace, a role failure should return forbidden.

Rule: outside accessible workspace -> `404`; inside accessible workspace but role lacks permission -> `403`.

Nested routes must verify the parent-child relationship, not just authenticate the user or check the parent in isolation.

#### Exercise and validation observations
Learner wrote a permission matrix with owner/admin/member/outsider roles. Corrections: creating a workspace is not a workspace-role permission because the workspace does not exist yet; any authenticated user can create their own workspace and become owner. Admin member removal should be constrained to lower-privilege members and must not remove an owner or last owner.

Learner correctly identified two nested-route attack cases: swapping both `project_id` and `task_id` from another workspace, and keeping an accessible project ID while swapping in a task ID from another workspace. Correct behavior is `404`, with lookups enforcing `task.id`, `task.project_id`, and project workspace membership together.

#### My questions, corrections, and revision items
Continue reinforcing the difference between cross-tenant invisibility (`404`) and in-tenant role denial (`403`). Build must remove the default-workspace bridge from authenticated project/task operations.
