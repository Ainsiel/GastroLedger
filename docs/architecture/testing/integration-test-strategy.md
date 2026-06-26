# Integration Test Strategy

```text
primary_boundary = FastAPI application + PostgreSQL
external_systems = none
environment = isolated per test worker
```

## Real Collaborators

- FastAPI application and application composition root;
- PostgreSQL with production migrations, constraints and RLS policies;
- PostgreSQL jobs/outbox worker;
- Next.js/FastAPI generated contract compatibility for selected workflows.

## Controlled Substitutes

- fixed clock;
- deterministic identifiers where needed;
- local session and TOTP fixtures;
- in-memory CSV byte streams;
- no third-party mocks because no third-party systems exist.

## High-Risk Boundaries

| Boundary | Risk proved |
|---|---|
| Session -> FastAPI -> RLS | Tenant and branch isolation |
| Procurement -> Inventory ledger | Receipt/return atomicity and idempotency |
| Menu -> Inventory allocation | Versioned recipe and unit conversion correctness |
| Concurrent commands -> PostgreSQL | No negative stock and deterministic conflicts |
| Sales import -> worker -> ledger | Partial success, exceptions and retry safety |
| Jobs/outbox -> consumers | Lease, retry, ordering assumptions and idempotency |
| Next.js -> FastAPI contract | Stable errors, decimals and visible incomplete states |

## Suite Separation

- Unit: domain policy, conversion, recipe cycle, cost and FEFO decisions.
- Integration: real PostgreSQL, transactions, RLS, repositories, jobs and HTTP.
- Contract: OpenAPI transport shapes and frontend consumer mappings.
- End-to-end: small set of critical visible workflows.
- Performance: measured later from accepted baseline, not guessed during design.

## Evidence

Failures must record correlation ID, tenant/test identifier, command/event ID,
database constraint or application problem code, and deterministic reproduction
steps without secrets.
