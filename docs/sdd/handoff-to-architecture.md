# SDD Handoff To Architecture

```text
status = accepted for simulation
next_agent = software-architect
next_workflow = architecture-ddd
```

## Architectural Drivers

- Shared SaaS deployment with strict tenant isolation.
- Deterministic and traceable inventory ledger.
- Decimal conversions, recipe explosion, yield and cost snapshots.
- Transactionally safe lot movements and no negative stock.
- Idempotent bounded imports and asynchronous recalculation.
- No external APIs or real-money workflows.
- Moderate V1 scope and operational simplicity.

## Required Architecture Outputs

- context ownership and language;
- multi-tenant isolation design;
- inventory, costing and recipe consistency rules;
- API and frontend boundaries;
- relational model and integration-test strategy;
- monorepo, local environment and rollback constraints;
- ADRs and backlog/foundation handoff;
- no HTML diagram artifacts.
