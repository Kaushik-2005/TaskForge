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
