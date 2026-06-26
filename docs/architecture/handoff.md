# Architecture Handoff

```text
status = ready for architecture approval
recommended_next_workflow = repository-bootstrap
following_workflow = architecture-foundation
```

## Inputs For Bootstrap

- Next.js web, FastAPI API/worker and PostgreSQL monorepo boundaries.
- No external APIs, broker, Redis, object store or payment infrastructure.
- Compose environment contract and isolated integration-test requirement.
- Exact versions and tooling remain to be detected/selected in bootstrap.

## Inputs For Architecture Foundation

- Six bounded contexts and dependency rules.
- Contract-before-behavior use-case policy.
- Tenant context, authorization, transactions, audit, jobs/outbox and ledger ports.
- Shared-schema RLS and 54-relation logical data model.
- Frontend route/feature boundaries and typed API consumption.
- Architecture, RLS, migration and integration-test requirements.

## Must Not Be Materialized As Product Behavior

- Recipe explosion, allocation, costing or any use-case logic.
- Real-money, subscription, accounting or payroll workflows.
- External API clients.
- Feature implementations without approved work orders.
