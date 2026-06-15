# Foundation And Vertical Slice Plan

```text
status = local draft only
github_issues_published = false
```

## Foundation Before Features

1. Bootstrap Next.js, FastAPI API/worker and PostgreSQL monorepo boundaries.
2. Materialize six backend module skeletons and frontend feature boundaries.
3. Define tenant context, session, authorization, transaction, audit, jobs and
   outbox contracts.
4. Add architecture conformance and isolated PostgreSQL integration-test harness.
5. Keep all use-case interactors empty until assigned feature work orders.

## Ordered Vertical Slices

| Order | Slice | Use cases | Why now |
|---:|---|---|---|
| 1 | Tenant registration and isolation tracer | UC-001, UC-003 | Proves SaaS/security architecture |
| 2 | Branch, units and ingredient setup | UC-004 to UC-006 | Enables all operational data |
| 3 | Recipe version and costing tracer | UC-008 to UC-010 | Proves core menu model |
| 4 | Supplier receipt to inventory ledger | UC-007, UC-013 | Proves cost and stock truth |
| 5 | Production batch | UC-011 | Proves conversion/yield/lot behavior |
| 6 | Transfer, waste and physical count | UC-015 to UC-020 | Completes inventory controls |
| 7 | Sales import and allocation exceptions | UC-021 | Proves recipe explosion at scale |
| 8 | Purchasing and supplier returns | UC-012, UC-014 | Completes procurement workflow |
| 9 | Cash and workforce operations | UC-022, UC-023 | Adds supporting branch workflows |
| 10 | Franchise controls and analytics | UC-024, UC-025 | Builds on trusted source facts |

Every feature issue must include UI, API, domain, persistence and tests when needed,
remain inside one primary context where feasible, and explicitly depend on foundation.

Every issue with frontend scope must also satisfy
`docs/backlog/frontend-delivery-contract.md`. It is not ready for implementation
without route ownership, shadcn/ui usage, applicable visible states, responsive and
accessibility expectations, frontend tests and visual QA evidence.
