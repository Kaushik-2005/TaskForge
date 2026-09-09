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


