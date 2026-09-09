# Backend Systems — Four-Week Project Roadmap

Prepared for Kaushik • Research checked: 7 September 2026

## Goal and pacing

Build **TaskForge**, a multi-user project/task backend, and learn to independently design, implement, test, debug, and explain it.

Allocate **3–4 focused hours per learning day: 84–112 hours total**. A day is a learning module, not an inflexible calendar deadline. If it takes longer, continue it and shift subsequent days. Four weeks provides a substantial foundation and production engineering practice, not mastery of every backend specialty.

Daily rhythm: 45–60 minutes selected reading/theory; 20–30 minutes questions and exercise; 90–120 minutes project work and validation; 15–30 minutes notes. Read the listed sections, not every chapter example in every language. Full chapter readings plus implementation would exceed this budget.

Assumptions: you know Python, basic Git/terminal use, and introductory APIs/AWS. Assess SQL/networking knowledge rather than assuming it. Choose one consistent Windows-native or WSL2 environment and record the shell. Do not switch environments midway without recording setup changes.

## Research basis

[Backend from First Principles](https://backend-from-first-principle.vercel.app/) is the teaching spine, abbreviated **BFP** below. All 24 chapters are mapped in the reading index. The sequence deliberately introduces configuration/testing early, persistence before full authentication, and database concurrency before workers.

The schedule and project are curriculum design recommendations. BFP is a learning reference; primary documentation governs precise behavior:

- [RFC 9110][HTTP] grounds methods, statuses, and protocol semantics. Stateless HTTP does not forbid application state or server-side sessions.
- [PostgreSQL isolation][ISO] and [query plans][PLAN] ground database experiments.
- [OWASP authorization][AUTHZ] supports explicit permissions and cross-user access checks.
- [AWS transactional outbox][OUTBOX] explains the database/event dual-write problem; consumers must still handle duplicates.
- [Google SRE SLOs][SLO] and [OpenTelemetry][OTEL] ground measurement and diagnosis. A brief load test cannot prove monthly availability.

## Project and stack

### User stories

1. Register, sign in, create a workspace, and add existing users as members.
2. Create projects/tasks; update status; list and search authorized tasks.
3. Request a CSV export, poll progress, and download it securely.
4. Subscribe to task updates through a small real-time lab.
5. Diagnose errors, recover jobs, drain services, and restore data.

### Architecture

One modular monolith repository; separate API and worker processes share domain code and PostgreSQL. Redis is a disposable cache and rate limiter. A PostgreSQL jobs table provides durable work. Use CLI requests and a tiny test client; no full frontend required.

| Component | Default | Learning purpose |
| --- | --- | --- |
| API | Python, FastAPI, Pydantic, Uvicorn | HTTP contracts, validation, boundaries |
| Persistence | PostgreSQL, SQLAlchemy, psycopg, Alembic | SQL, constraints, migrations, transactions |
| Initial execution | Synchronous DB calls in synchronous handlers | Understand blocking work before introducing async |
| Identity | Opaque sessions in PostgreSQL; maintained password hashing library | Expiry, revocation, cookie security |
| Acceleration | Redis, introduced Day 12 | Cache correctness and shared limits |
| Jobs | PostgreSQL jobs table and bounded worker | Claims, leases, retry/recovery |
| Verification | pytest, HTTPX, Ruff; Locust later | Behavior, integration, load experiments |
| Operations | Docker Compose, GitHub Actions, OpenTelemetry | Repeatable release and diagnosis |
| Export storage | Private persistent local volume | Avoid requiring cloud credentials |

Resolve compatible, supported versions when starting and lock dependencies. Do not install all tools on Day 1. Go is an optional alternate language only if you choose it; preserve the same daily outcomes and record the change. Do not implement both versions during these four weeks.

### Data and invariants

Introduce tables as needed: users, sessions, workspaces, memberships, projects, tasks, audit_events, idempotency_keys, jobs, exports.

- Membership proves access; a client-supplied workspace ID does not.
- Parent/child resources must belong to the authorized workspace.
- Task states: todo, in_progress, done; store a version for conditional updates.
- Writes that must succeed together share a transaction.
- An export request and its durable job commit together.
- Execution may repeat; stable operation IDs and conditional finalization prevent duplicate visible artifacts.
- PostgreSQL is authoritative. Redis must not become the only copy of important data.
- Do not cache authorization decisions in the first implementation.

**Build/test deeply:** HTTP, SQL, identity, tenant isolation, transactions, indexes, pagination, caching, rate limits, durable jobs, concurrency, resilience, telemetry, shutdown, CI, backup/restore.

**Focused lab/design depth:** WebSockets, gRPC, Kafka, Elasticsearch, Kubernetes, S3, replication, sharding, CAP, distributed workflows. Cover their trade-offs without operating every technology.

## Learning records and daily design history

Keep roadmap.md, AGENTS.md, and README.md at the repository root. Maintain these records in the repository’s docs/ folder:

| File | Responsibility |
| --- | --- |
| docs/tracker.md | Progress, evidence, blockers, exact resume point |
| docs/learning.md | Concepts, examples, readings, corrections |
| docs/session-log.md | Session activities and next-session handoff |
| docs/decisions.md | Architecture decisions, alternatives, and rationale |
| docs/design.md | Current architecture snapshot and chronological daily design changes |

Every day includes a docs/design.md update within the notes budget. Follow the attached reference's structure: purpose/principles, current layers, actual file ownership, capabilities, meaningful flow diagrams, then daily changes, boundary placement, verification, and limitations. Link significant choices to docs/decisions.md. On review-only days, explicitly record no runtime architecture change and capture verification or clarified boundaries.

The snapshot describes implemented reality; label plans and unverified behavior separately. Append history only for days actually attempted. Continue an in-progress day's entry across sessions, preserve past design states, and use dated follow-ups for later revisions. docs/design.md must not claim project implementation before code and evidence exist.

Migrate existing root learning records into docs/ without losing history; reconcile duplicates before choosing one authoritative record. Detailed instructions and the daily entry format are in AGENTS.md.

## Day-by-day map

| Day | Module | Main result |
| --- | --- | --- |
| 1 | W1.1 Request journey and environment | Trace a request; run health endpoint |
| 2 | W1.2 Routing and API contracts | Resource API and contract tests |
| 3 | W1.3 Serialization and validation | Consistent input/output boundaries |
| 4 | W1.4 Layers and configuration | HTTP/domain/persistence separation |
| 5 | W1.5 Relational modeling and SQL | Schema, constraints, queries |
| 6 | W1.6 Persistence and migrations | Durable CRUD and integration tests |
| 7 | W1.7 Foundation review | Fresh-start CRUD demonstration |
| 8 | W2.1 Authentication and sessions | Login, expiry, logout |
| 9 | W2.2 Authorization and isolation | Membership/role enforcement |
| 10 | W2.3 Transactions and concurrent writes | Prevent silent lost updates |
| 11 | W2.4 Indexes and query performance | Measured query improvement |
| 12 | W2.5 Cache correctness | Cache with explicit freshness policy |
| 13 | W2.6 Security and resource limits | Threat model and shared rate limits |
| 14 | W2.7 Correctness review | Security/race/cache scenario pack |
| 15 | W3.1 Durable background jobs | Accepted, persistent export job |
| 16 | W3.2 Concurrency and ownership | Bounded workers and recoverable leases |
| 17 | W3.3 Idempotency and retries | Duplicate/crash recovery |
| 18 | W3.4 Search and files | Authorized search/download |
| 19 | W3.5 Dependency resilience | Deadlines and circuit-breaker lab |
| 20 | W3.6 Real-time and communication | WebSocket lab; RPC/event comparison |
| 21 | W3.7 Recovery review | Failure-injection demonstration |
| 22 | W4.1 Observability and SLOs | Trace and diagnose an operation |
| 23 | W4.2 Load and capacity | Measured bottleneck and improvement |
| 24 | W4.3 Scaling trade-offs | Two API instances and growth design |
| 25 | W4.4 Packaging and shutdown | Reproducible image; bounded drain |
| 26 | W4.5 CI and release safety | Automated gates and rollback rehearsal |
| 27 | W4.6 Deployment and recovery | Local release; verified restore |
| 28 | W4.7 Capstone review | Demo, design defense, limitations |

## Week 1 — Requests, structure, and durable data

### Day 1 — W1.1: Request journey and environment

**Read:** BFP 01: message anatomy, transport, TLS, methods, debugging; BFP 14: settings basics. Primary: [HTTP semantics][HTTP].

**Learn:** DNS, ports/sockets, TCP versus QUIC, TLS termination, reverse proxies, process/thread basics, environment variables, and request/response headers. Separate transport behavior from application state.

**Exercise:** Annotate a verbose curl exchange and locate DNS, connection, TLS, and application failures on the request path.

**Build:** Only the API skeleton, environment settings, example configuration without secrets, health/live endpoint, and one HTTP smoke test. Write an initial project contract. Initialize learning records using AGENTS.md and establish the actual baseline in docs/design.md.

**Completion:** A documented command starts the server; health test passes; explain each network hop and why a stateless protocol can support sessions. No secrets in Git.

### Day 2 — W1.2: Routing and API contracts

**Read:** BFP 02; selected BFP 07 resource/method/status/pagination sections. Primary: [RFC 9110][HTTP].

**Learn:** Resources, path/query parameters, safe/idempotent methods, PUT/PATCH, 401/403/404/409, versioning, pagination bounds, and error contracts.

**Exercise:** Write an endpoint table with requests, responses, and failures. Explain why repeated idempotent operations can return different status codes.

**Build:** In-memory project/task CRUD, initial OpenAPI contract, bounded list limit, explicit ordering, and consistent error envelope. Reserve /api/v1 without building multiple versions.

**Completion:** HTTP tests cover create/read/update/delete, missing resource, wrong method, and page-size bounds. Explain your PUT/PATCH semantics.

### Day 3 — W1.3: Serialization and validation

**Read:** BFP 03 and BFP 05: JSON, type conversion, validation layers, response models.

**Learn:** Missing versus null, UTC timestamps, strict/coercing input, schema versus domain validation, field allowlists, and sensitive output exclusion.

**Exercise:** Classify malformed JSON, invalid UUID, oversized title, forbidden state change, and an unexpected workspace field by rejecting layer.

**Build:** Separate create/update/read models; accept only editable fields; add payload limits and explicit patch semantics. Keep important business rules outside transport-only models.

**Completion:** Tests cover empty/oversized values, malformed payloads, unknown fields, null/missing updates, and response leakage. Explain why parsing successfully does not imply validity.

### Day 4 — W1.4: Layers and configuration

**Read:** BFP 06; BFP 14 settings precedence/startup validation; BFP 12 error classification.

**Learn:** Handlers, services, repositories, dependency injection, middleware ordering, resource lifetime, and domain/infrastructure errors.

**Exercise:** Trace a task update through each layer; move one misplaced business rule out of a handler.

**Build:** Small cohesive modules, request IDs, basic structured logs, exception mapping, and validated startup configuration. Add service tests without HTTP.

**Completion:** Invalid config prevents startup; public errors omit tracebacks; logs omit bodies/credentials; explain which rules need object-level context rather than generic middleware.

### Day 5 — W1.5: Relational modeling and SQL

**Read:** BFP 08: modeling, constraints, queries, transaction overview. Supplement: [PostgreSQL isolation][ISO].

**Learn:** Primary/foreign/unique/check constraints, normalization, joins, aggregates, NULL, parameterized SQL, and relational versus document/key-value trade-offs.

**Exercise:** Draw the ER model and write member-task and per-project-count queries. Demonstrate an incorrect join.

**Build:** PostgreSQL in local Compose, initial migration for workspace/project/task data and membership, synthetic seed data. Keep the unauthenticated development API local.

**Completion:** Database rejects broken relationships and duplicate memberships; queries handle empty projects. Explain why constraints are needed when API validation exists.

### Day 6 — W1.6: Persistence and migrations

**Read:** BFP 08 database access; BFP 22 integration tests/fixtures.

**Learn:** Connection pools, request-scoped DB sessions, commit/rollback, migrations, N+1 query awareness, and isolated test databases.

**Exercise:** Fail halfway through a multi-step write and inspect persisted state. Identify a connection leak.

**Build:** Replace memory storage with PostgreSQL repositories using SQLAlchemy/psycopg. Configure finite pool capacity/wait time; run migrations separately from requests. Test against real PostgreSQL.

**Completion:** Restart preserves data; migration from empty succeeds; failed work rolls back; tests cannot target developer data. Explain total pool demand across processes.

### Day 7 — W1.7: Foundation review

**Read:** Weak sections from Days 1–6; BFP 22 test boundaries.

**Exercise:** Five conceptual questions; debug a broken query; implement a small filtered endpoint without a complete generated solution.

**Build:** Finish durable CRUD, migration, contract, setup guide, and HTTP/service/database checks. Remove obsolete memory-only production paths.

**Completion:** Fresh checkout setup works and you can explain the write path and failures. Save evidence and a short architecture decision. Unfinished understanding remains incomplete.

## Week 2 — Identity, correctness, performance, and security

### Day 8 — W2.1: Authentication and sessions

**Read:** BFP 04 sessions/cookies/JWT/OAuth/OIDC. Primary: [OWASP sessions][SESSION], [password storage][PASSWORD].

**Learn:** Authentication, password hashing, session rotation/expiry/revocation, cookie flags, CSRF, and token signing versus encoding. OAuth/OIDC are comparison topics.

**Exercise:** Trace login, expiry, logout, and session theft; explain hashing versus encryption.

**Build:** Registration/login/logout/me, maintained Argon2id-capable hashing library, unpredictable opaque session IDs, and server-side expiry. Protect cookie-authenticated mutations from CSRF immediately.

**Completion:** Wrong credentials, expired/revoked sessions, rotation, and CSRF are tested. Validate secure cookies in the HTTPS release profile; document local HTTP exception. Explain your session choice.

### Day 9 — W2.2: Authorization and tenant isolation

**Read:** BFP 04 authorization; BFP 17 access control. Primary: [OWASP authorization][AUTHZ].

**Learn:** Deny by default, ownership/membership relationships, roles, object-level access, and tenant-aware queries.

**Exercise:** Write an owner/member/outsider permission matrix. Attack nested routes using another workspace's project/task ID.

**Build:** Membership management for existing users and authorization on every data path. Scope repositories explicitly and verify parent-child ownership.

**Completion:** Two-user/two-workspace tests block cross-tenant read/write/list, self-enrollment, and role escalation. Extend these checks as jobs/search/real-time arrive. Explain authentication versus permission.

### Day 10 — W2.3: Transactions and concurrent writes

**Read:** BFP 08 transactions; BFP 20 races. Primary: [PostgreSQL isolation][ISO].

**Learn:** ACID, MVCC, read committed/repeatable read/serializable, row locks, deadlocks, optimistic concurrency, and transaction retries.

**Exercise:** Reproduce a lost update with two DB sessions; compare locking and version-checked writes.

**Build:** Conditional task updates and audit events in one transaction. Choose a version-based 409 or HTTP-precondition 412 contract and document it.

**Completion:** Same-version concurrent updates cannot silently overwrite each other; update/audit rollback together. Explain why merely using a transaction does not remove all anomalies.

### Day 11 — W2.4: Indexes and query performance

**Read:** BFP 08 indexes; BFP 18 DB bottlenecks. Primary: [PostgreSQL EXPLAIN][PLAN].

**Learn:** Selectivity, composite index order, sort cost, scans, N+1, offset/keyset pagination.

**Exercise:** Seed approximately 10,000 tasks, reduce if needed. Inspect EXPLAIN (ANALYZE, BUFFERS) on a disposable DB; ANALYZE executes the query.

**Build:** A workload-driven index and deterministic cursor pagination with a tie-breaker such as created_at plus ID. Allowlist sorting.

**Completion:** Record plans/timing before and after; test ties, malformed cursors, and tenant filters. Document concurrent-data-change limitations of pagination. Explain why a planner might ignore an index.

### Day 12 — W2.5: Cache correctness

**Read:** BFP 09; primary [Redis cache-aside][CACHE].

**Learn:** Cache-aside, TTL, invalidation, eviction, hot keys, stampedes, and freshness versus correctness.

**Exercise:** Draw how a concurrent read can repopulate stale data after invalidation; choose an acceptable stale-data window.

**Build:** Cache one non-sensitive project summary after authorization. Include tenant/resource/schema version in the key; expire entries and invalidate after committed writes. Fall back to PostgreSQL on bounded Redis failure.

**Completion:** Test hit/miss/expiry/update/outage and tenant isolation. Document the residual stale-fill race; do not claim strict consistency. Explain why TTL and invalidation complement each other.

### Day 13 — W2.6: Security and resource limits

**Read:** BFP 17 injection/SSRF/secrets/abuse; BFP 01 CORS. Revisit [OWASP authorization][AUTHZ].

**Learn:** Threat modeling, SQL injection, CSRF versus CORS, trusted proxy headers, request bounds, secret handling, and shared throttling.

**Exercise:** Identify assets, attackers, trust boundaries, and abuse cases. Explain why CORS does not stop curl clients.

**Build:** Atomic Redis rate limits with expiry, user/IP keys, 429 behavior, and explicit outage policy. Review login throttling, payload/page limits, CORS, and log redaction. Do not fetch arbitrary user URLs.

**Completion:** Parallel calls cannot trivially bypass limits; test outage policy and spoofed headers. Explain fail-open versus fail-closed decisions for distinct dependencies.

### Day 14 — W2.7: Correctness review

**Exercise:** Five questions on identity, permissions, transactions, indexing, caching; debug a tenant leak; implement a protected operation.

**Build:** Scenario pack: expired session, swapped workspace IDs, stale version, DB rollback, Redis outage, oversized input. Compare actual routes with the permission matrix.

**Completion:** No known cross-tenant exposure; each scenario has evidence. Deliver a query-plan report, threat model, and cache policy. Explain where session, durable, and cached state live.

## Week 3 — Background work and unreliable dependencies

### Day 15 — W3.1: Durable background jobs

**Read:** BFP 10 queue/job lifecycle.

**Learn:** Durable acceptance, polling, claim/complete, attempts, leases, terminal failure, and process-local callback limitations.

**Exercise:** Sketch pending/running/succeeded/failed states and possible crashes at each boundary.

**Build:** Export request returns 202 plus status URL only after export/job records commit together. Add one worker, small CSV generation, and authorized status lookup. Harden leasing tomorrow.

**Completion:** Pending work survives API restart; success/failure are inspectable. Explain the exact point at which accepted work is retained.

### Day 16 — W3.2: Concurrency and lifecycle ownership

**Read:** BFP 20; BFP 16 cancellation basics. Primary: [FastAPI async][ASYNC].

**Learn:** I/O versus CPU, event-loop blocking, threads/processes, semaphores, bounded worker pools, lease ownership, and cancellation.

**Exercise:** Compare sequential/bounded concurrent waits; show a blocking call stalling an event loop in an isolated script.

**Build:** Short atomic job claims using PostgreSQL FOR UPDATE SKIP LOCKED; work outside the claim transaction. Add lease ownership tokens, renewal/expiry, conditional completion, and bounded concurrency.

**Completion:** Two workers do not initially claim the same available job; expired owners cannot overwrite newer claims. Explain why execution can still repeat after lease loss, and why process-local locks cannot coordinate separate workers.

### Day 17 — W3.3: Idempotency and reliable retries

**Read:** BFP 10/12 retry sections; BFP 23 outbox. Primary: [AWS outbox][OUTBOX], [backoff and jitter][JITTER].

**Learn:** Request deduplication, payload fingerprints, replay semantics, retryable/permanent failures, jitter, maximum attempts, and dual writes.

**Exercise:** Analyze crashes before commit, after commit/before response, and after file creation/before job completion.

**Build:** Scope idempotency keys to user/workspace/operation; reject key reuse with changed payload. Add bounded retries and failure inspection. Finalize a stable export artifact from a temporary path safely.

**Completion:** Concurrent duplicates create one logical export; crash/retry does not expose duplicate outputs. Current DB jobs avoid a broker dual-write; design an outbox for a future broker. Explain why delivery guarantees do not automatically cover external effects.

### Day 18 — W3.4: Search and files

**Read:** BFP 11 search/relevance; primary [PostgreSQL full-text search][SEARCH], [S3 presigned URLs][S3].

**Learn:** Inverted indexes, token search, ranking, search freshness, object storage versus metadata, expiring capabilities, path traversal, and CSV formula injection.

**Exercise:** Compare substring/full-text/semantic search. Design private S3 upload/download authorization without provisioning cloud resources.

**Build:** Authorized PostgreSQL task search with an appropriate index; private CSV download with server-generated paths, formula-safe fields, retention/cleanup rules.

**Completion:** Search/download cannot cross tenants; traversal and expired artifacts fail consistently. Explain when Elasticsearch warrants a second index and its synchronization cost.

### Day 19 — W3.5: Dependency resilience

**Read:** BFP 12; BFP 13 deadlines. Primary: [gRPC deadlines][DEADLINE], [AWS jitter][JITTER].

**Learn:** Timeout budgets, retry amplification, circuit states, bounded half-open probes, bulkheads, and degradation.

**Exercise:** Calculate retry multiplication across layers; allocate connection/operation budgets within a request deadline.

**Build:** A controllable mock dependency adapter for a resilience lab, separate from the critical project path. Exercise slow responses, timeouts, 429/5xx, and recovery; implement/configure a small circuit breaker and one retry owner.

**Completion:** Calls stop at finite budgets; breaker opens/recovers in fake-clock tests. Explain why timeout does not prove the remote side did nothing.

### Day 20 — W3.6: Real-time and communication choices

**Read:** Selected BFP 24 connection/backpressure, BFP 13 contracts, BFP 23 ordering/replay. Primary: [gRPC deadlines][DEADLINE], [Kafka design][KAFKA].

**Learn:** Polling/SSE/WebSocket, REST/gRPC, request-response versus events, partitions/groups/offsets, and schema evolution.

**Exercise:** Choose protocols for three TaskForge interactions; design a task.updated event and explain ordering boundaries.

**Build:** Small authenticated WebSocket update lab/client: authorize workspace subscription, validate browser Origin, bound buffers, clean disconnects. In-process delivery is a single-instance lab; polling remains reliable status retrieval.

**Completion:** Unauthorized/slow/disconnected clients behave predictably. Document refetch-on-reconnect and multi-instance limitations. gRPC/Kafka require a reasoned comparison, not deployment today.

### Day 21 — W3.7: Recovery review

**Exercise:** Five questions on leases/duplicates/retries/search/connections; debug a stuck job; implement one recovery case.

**Build:** Run two workers, kill one during export, replay the request, restart it, and inject Redis/mock dependency failures.

**Completion:** Accepted work recovers, one logical output is visible, retries stay bounded. Deliver a failure matrix: injection, expected behavior, actual result, evidence, remaining risks. Do not infer universal losslessness or exactly-once operation from these tests.

## Week 4 — Operating and shipping

### Day 22 — W4.1: Observability and SLOs

**Read:** BFP 15; primary [OpenTelemetry][OTEL], [Google SRE SLOs][SLO].

**Learn:** Logs/metrics/traces, spans, propagation, histograms/percentiles, sampling, metric cardinality, SLIs/SLOs/error budgets.

**Exercise:** Identify the signals needed to distinguish slow SQL, queue delay, and slow dependencies.

**Build:** Measure HTTP duration/error rate, DB calls, job age/attempts/duration, cache behavior. Correlate request-to-job via persisted trace context or span links. Start with a console exporter or local telemetry backend.

**Completion:** Save a trace and metric query that localize a delay; no secrets or unbounded user-ID labels. Specify a proposed SLO's window, numerator/denominator, exclusions, and response action. Explain average versus tail latency.

### Day 23 — W4.2: Load and capacity

**Read:** BFP 18/19 measurement/saturation; BFP 22 load testing; [query plans][PLAN].

**Learn:** Throughput, concurrency, latency, queueing, bottlenecks, resource saturation, and profiling.

**Exercise:** Estimate in-flight work as throughput times average latency under stable conditions. Explain the effect of unbounded queues.

**Build:** Reproducible Locust workload with authenticated users and a stated read/write/export mix. Ramp gradually; measure throughput, p50/p95/p99, failures, pool waits, CPU/memory, queue age. Fix one measured bottleneck and rerun.

**Completion:** Record hardware, versions, dataset, load model, warmup, duration, cold/warm cache, and before/after results. Set a lab target after baseline; do not invent an industry-standard RPS target.

### Day 24 — W4.3: Scaling trade-offs

**Read:** BFP 18/19 scaling/distribution; BFP 23 replay/schema evolution.

**Learn:** Load balancing, replicas, sharding, hot keys, consistency, CDN/object delivery, monolith/microservices, CAP during partitions, and saga compensation.

**Exercise:** Design for hypothetical 10× load. Estimate total DB connections; discuss replica read-after-write and compensation limits.

**Build:** Two API instances behind a local reverse proxy with shared DB/session/cache. Retain polling for reliable status across instances. Record when service extraction or broker/outbox would help.

**Completion:** Either instance serves the same session correctly without unbounded pool demand. Explain the bottleneck that extra API instances cannot fix. Sharding, brokers, and microservices remain design exercises.

### Day 25 — W4.4: Packaging and shutdown

**Read:** BFP 16/21; primary [Docker practices][DOCKER], [Kubernetes probes][PROBES].

**Learn:** Images/layers, non-root runtime, persistent volumes, signals, readiness/liveness/startup, and drain deadlines.

**Exercise:** Walk through termination with an active request and job. Explain why DB downtime should not necessarily trigger repeated liveness restarts.

**Build:** Finalize image/Compose, readiness, and shutdown. Stop accepting new work and claiming jobs; drain or relinquish safely; close resources within a deadline.

**Completion:** SIGTERM behavior matches policy and work is recoverable; export storage survives restart. Kubernetes deployment/service/probe sketches are optional implementation depth; explain probe concepts regardless.

### Day 26 — W4.5: CI and release safety

**Read:** BFP 21 pipeline/rollout; BFP 22 contracts/regressions. Primary: [GitHub Actions Python][CI], [Docker practices][DOCKER].

**Learn:** Reproducible builds, dependency checks, API compatibility, expand/migrate/contract, and rollback boundaries.

**Exercise:** Plan a safe column rename and classify an API field removal as a contract break.

**Build:** CI lint, behavioral tests, PostgreSQL integration, empty-DB migration, image build, dependency vulnerability checks. Add a compatibility gate exercised by a deliberately breaking schema fixture. Pin dependencies and review CI action revisions.

**Completion:** Clean CI passes and the breaking fixture fails the intended gate. Rehearse previous-image rollback against a compatible schema locally. Explain why old application code cannot undo data loss.

### Day 27 — W4.6: Deployment and recovery

**Read:** BFP 21 deployment; BFP 14 environment separation; [PostgreSQL backup/restore][BACKUP].

**Learn:** Ingress/TLS, secrets, least-privilege credentials, persistence, RPO/RTO, and restore verification.

**Exercise:** State effects of losing DB, Redis, or export volume; define measurable lab recovery goals.

**Build:** Run the built release in a fresh local Compose environment with release configuration. Back up and restore into a separate empty database; verify users/memberships/tasks/jobs. Document separate export-volume recovery.

**Completion:** Release smoke tests and restore checks pass; record recovery time and runbook. Cloud deployment is optional with a supplied target and resource authorization; otherwise document an AWS layout and cost drivers without provisioning. A successful backup command alone is not recovery proof.

### Day 28 — W4.7: Capstone review

**Exercise:** Five questions from weak areas, one unseen bug, one independent small feature.

**Build:** Demo login → workspace/task → denied cross-tenant access → conflicting update → export → worker failure/recovery → authorized download → trace diagnosis.

**Completion:** Deliver README, architecture/ER diagrams, OpenAPI, permission matrix, threat model, decisions, migration/recovery runbook, performance report, failure matrix, and known limitations. Reconcile docs/design.md with the code and daily history. Give a ten-minute design defense with three rejected alternatives. Record weaknesses and choose the next extension from evidence.

## Weekly gates

| Week | Milestone | Required evidence |
| --- | --- | --- |
| 1 | Durable validated CRUD | API examples, SQL exercise, migration, HTTP/integration checks |
| 2 | Isolated multi-user API | Permission matrix, race tests, plans, security/cache scenarios |
| 3 | Recoverable asynchronous work | Duplicate/crash tests, failure matrix, communication comparison |
| 4 | Operated reproducible release | CI result, trace, load report, shutdown/restore drills, walkthrough |

Each gate includes five conceptual questions, one debugging exercise, and one implementation exercise. Completion requires reading, demonstrated understanding, exercise, applicable build/lab, validation evidence, and an up-to-date daily design entry and snapshot. Optional extensions do not block completion. Generated implementation alone is not demonstrated understanding.

## BFP chapter-to-day reading index

Use daily topic lists to select sections. This table maps all chapters, not a requirement to implement all chapter technologies.

| Chapter | Direct reading | Days | Depth |
| --- | --- | --- | --- |
| 01 | [HTTP & CORS](https://backend-from-first-principle.vercel.app/01-http-and-cors/) | 1, 2, 13 | Core |
| 02 | [Routing](https://backend-from-first-principle.vercel.app/02-routing-in-backend/) | 2 | Core |
| 03 | [Serialization](https://backend-from-first-principle.vercel.app/03-serialization-and-deserialization/) | 3 | Core |
| 04 | [Authentication & Authorization](https://backend-from-first-principle.vercel.app/04-authentication-and-authorization/) | 8, 9 | Core; OAuth/OIDC comparison |
| 05 | [Validation](https://backend-from-first-principle.vercel.app/05-validations-and-transformations/) | 3 | Core |
| 06 | [Controllers, Services & Middleware](https://backend-from-first-principle.vercel.app/06-controllers-services-and-middlewares/) | 4 | Core |
| 07 | [REST Design](https://backend-from-first-principle.vercel.app/07-api-design-rest/) | 2 | Core |
| 08 | [Databases](https://backend-from-first-principle.vercel.app/08-databases/) | 5, 6, 10, 11 | Core |
| 09 | [Caching](https://backend-from-first-principle.vercel.app/09-caching/) | 12 | Core |
| 10 | [Queues](https://backend-from-first-principle.vercel.app/10-task-queues-and-background-jobs/) | 15–17 | Core |
| 11 | [Search](https://backend-from-first-principle.vercel.app/11-full-text-search-elasticsearch/) | 18 | PostgreSQL build; Elasticsearch comparison |
| 12 | [Fault Tolerance](https://backend-from-first-principle.vercel.app/12-error-handling-and-fault-tolerance/) | 4, 17, 19 | Core |
| 13 | [gRPC](https://backend-from-first-principle.vercel.app/13-grpc-and-inter-service-communication/) | 19, 20 | Deadlines and comparison |
| 14 | [Configuration](https://backend-from-first-principle.vercel.app/14-configuration-management/) | 1, 4, 27 | Core |
| 15 | [Observability](https://backend-from-first-principle.vercel.app/15-logging-and-observability/) | 22 | Core; logs start Day 4 |
| 16 | [Shutdown](https://backend-from-first-principle.vercel.app/16-graceful-shutdown/) | 16, 25 | Core |
| 17 | [Security](https://backend-from-first-principle.vercel.app/17-backend-security/) | 9, 13 | Core; safe defaults throughout |
| 18 | [Scaling 1](https://backend-from-first-principle.vercel.app/18-scaling-and-performance-part-1/) | 11, 23, 24 | Measurement/design |
| 19 | [Scaling 2](https://backend-from-first-principle.vercel.app/19-scaling-and-performance-part-2/) | 23, 24 | Capacity/design |
| 20 | [Concurrency](https://backend-from-first-principle.vercel.app/20-concurrency-and-parallelism/) | 10, 16 | Core |
| 21 | [Docker, K8s & CI/CD](https://backend-from-first-principle.vercel.app/21-docker-k8s-and-ci-cd/) | 25–27 | Docker/CI build; K8s concepts |
| 22 | [Testing](https://backend-from-first-principle.vercel.app/22-automated-testing/) | 6, 7, 23, 26 | Core; starts Day 1 |
| 23 | [Brokers & Kafka](https://backend-from-first-principle.vercel.app/23-message-brokers-and-kafka/) | 17, 20, 24 | Ordering/replay/outbox design |
| 24 | [WebSockets](https://backend-from-first-principle.vercel.app/24-websockets-and-real-time/) | 20 | Bounded lab |

## Primary references

Read the topics linked in daily modules. These are maintainers' documentation or standards, supplementing BFP. Version-specific implementation must match the pinned environment; live current documentation can change. Kafka 4.1 is a versioned conceptual reference, not an installation recommendation.

- [HTTP semantics: RFC 9110][HTTP]
- [PostgreSQL transaction isolation][ISO]
- [PostgreSQL EXPLAIN][PLAN]
- [OWASP authorization][AUTHZ]
- [OWASP session management][SESSION]
- [OWASP password storage][PASSWORD]
- [Redis cache-aside][CACHE]
- [AWS transactional outbox][OUTBOX]
- [AWS exponential backoff and jitter][JITTER]
- [FastAPI concurrency and async][ASYNC]
- [PostgreSQL full-text search][SEARCH]
- [S3 presigned URLs][S3]
- [gRPC deadlines][DEADLINE]
- [Apache Kafka design and delivery semantics][KAFKA]
- [OpenTelemetry signals][OTEL]
- [Google SRE service-level objectives][SLO]
- [Docker build practices][DOCKER]
- [Kubernetes probes][PROBES]
- [GitHub Actions: Python][CI]
- [PostgreSQL SQL dump and restore][BACKUP]

[HTTP]: https://www.rfc-editor.org/rfc/rfc9110.html
[ISO]: https://www.postgresql.org/docs/current/transaction-iso.html
[PLAN]: https://www.postgresql.org/docs/current/using-explain.html
[AUTHZ]: https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html
[SESSION]: https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html
[PASSWORD]: https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html
[CACHE]: https://redis.io/docs/latest/develop/use-cases/cache-aside/
[OUTBOX]: https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html
[JITTER]: https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/
[ASYNC]: https://fastapi.tiangolo.com/async/
[SEARCH]: https://www.postgresql.org/docs/current/textsearch.html
[S3]: https://docs.aws.amazon.com/AmazonS3/latest/userguide/using-presigned-url.html
[DEADLINE]: https://grpc.io/docs/guides/deadlines/
[KAFKA]: https://kafka.apache.org/41/design/design/
[OTEL]: https://opentelemetry.io/docs/concepts/signals/
[SLO]: https://sre.google/sre-book/service-level-objectives/
[DOCKER]: https://docs.docker.com/build/building/best-practices/
[PROBES]: https://kubernetes.io/docs/concepts/workloads/pods/probes/
[CI]: https://docs.github.com/en/actions/tutorials/build-and-test-code/python
[BACKUP]: https://www.postgresql.org/docs/current/backup-dump.html

## Beyond four weeks

Choose based on actual weak areas: OAuth/OIDC provider integration; managed S3 exports; RabbitMQ/SQS/Kafka with outbox and replay; database replication/failover and PITR; Elasticsearch synchronization; Kubernetes deployments; multi-region consistency; advanced capacity planning. Real payment processing, consensus implementation, and operating large clusters are separate projects.

## Start in Codex

Place roadmap.md and AGENTS.md in the repository root. Say:

> Start roadmap. Read AGENTS.md and roadmap.md, initialize the missing learning records, inspect the repository, and begin Day 1 in guided learning mode. Teach one concept at a time and let me attempt exercises.

For a new session:

> Continue roadmap. Read the learning records and inspect the code. Resume the exact incomplete step without assuming prior chat context.

The agent initializes or maintains docs/tracker.md, docs/learning.md, docs/session-log.md, docs/decisions.md, and docs/design.md, preserving existing contents. docs/design.md is a required learning record described in AGENTS.md, not a prefilled completed-history file. No progress or implementation is pre-marked complete.
