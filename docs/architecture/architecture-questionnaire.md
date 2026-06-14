# Architecture Questionnaire

```text
status = answered with recommended defaults for simulation
approved_sdd = ../sdd/
```

| Topic | Recommended answer | Architecture impact |
|---|---|---|
| Core domain | Recipe-to-inventory traceability and cost variance | Inventory & Production plus Menu Engineering receive strongest domain modeling |
| Tenant topology | Shared database/shared schema with tenant key and RLS | Every tenant-owned transaction sets tenant context |
| Deployment | Modular monolith; API and worker from one backend codebase | Avoid premature microservices |
| Consistency | Strong consistency inside one inventory transaction; eventual projections/jobs | Ledger commits atomically, reports may lag |
| Stock policy | No negative stock; FEFO then FIFO | Allocation failures become explicit exceptions |
| Recipe model | Versioned recipes, maximum nesting depth 2 | Cycles rejected; deterministic explosion |
| Cost model | Moving weighted average by branch/ingredient plus recipe snapshots | Historical reports do not change retroactively |
| Imports | Bounded CSV/manual imports with preview and idempotency | No POS API, partial valid processing allowed |
| Identity | Local credentials, local sessions, optional TOTP | No external identity/email provider |
| Notifications | In-app only | Worker writes notification records |
| Async work | PostgreSQL jobs and transactional outbox | No broker in V1 |
| Reporting | PostgreSQL projections and bounded report queries | Dedicated warehouse deferred |
| Money | Decimal informational values, no financial transaction lifecycle | No payment, billing, ledger or accounting context |
| Availability | 99.5%, RPO 15m, RTO 4h | Simple deployment plus tested backups |

## Decisions Deferred

- Dedicated queue only after measured PostgreSQL queue contention.
- Dedicated analytics store only after reporting affects transactional SLOs.
- External integrations require a new SDD scope and ADR.
- Multi-currency requires confirmed business demand and explicit conversion source.
