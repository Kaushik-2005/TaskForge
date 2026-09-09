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
