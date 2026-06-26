# Dependency Rules

1. Domain policy has no dependency on FastAPI, Next.js, PostgreSQL or transport
   schemas.
2. Application use cases orchestrate domain policy, authorization, transactions and
   ports.
3. FastAPI routers map HTTP to commands/queries and never contain inventory or
   costing rules.
4. PostgreSQL adapters implement repositories owned by one bounded context.
5. Next.js owns presentation and interaction state; FastAPI owns authorization and
   business truth.
6. Contexts use published application contracts or outbox events, never another
   context's adapter or mutable table.
7. `shared` code may contain technical primitives and stable contract utilities, not
   business behavior.
8. Tenant context is mandatory before any tenant-owned repository operation.

## Conformance Checks For Foundation

- forbidden cross-context imports;
- domain imports no framework modules;
- routers import application public APIs only;
- frontend features cannot import another feature's internals;
- no tenant-owned repository call without tenant scope;
- no external HTTP client dependency without a new approved ADR.
