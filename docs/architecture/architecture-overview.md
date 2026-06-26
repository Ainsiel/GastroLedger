# Architecture Overview

## Style

GastroLedger uses a modular monolith. Next.js serves the web experience. One FastAPI
codebase exposes the API and a separate worker entry point. PostgreSQL owns
transactional truth, tenant isolation, jobs, outbox and initial reporting
projections.

```text
Browser
  -> Next.js Web
  -> FastAPI API
     -> Platform & Organization
     -> Menu Engineering
     -> Procurement
     -> Inventory & Production
     -> Store Operations
     -> Control & Insights
  -> PostgreSQL

FastAPI Worker
  -> PostgreSQL jobs/outbox
  -> invokes application use cases
  -> writes projections and in-app notifications
```

No runtime flow requires an external API. CSV import and open-format export cover
initial data exchange.

## Bounded Contexts

| Context | Purpose | Classification |
|---|---|---|
| Platform & Organization | Tenant, access, branch and warehouse scope | Generic critical |
| Menu Engineering | Units, ingredients, recipes, yield and theoretical cost | Core |
| Procurement | Supplier offers, orders, receipts and returns | Supporting |
| Inventory & Production | Lots, ledger, allocation, production, transfers, waste and counts | Core |
| Store Operations | Sales imports, cash shifts, workforce schedules and attendance | Supporting |
| Control & Insights | Royalty estimates, holds, reports, audit, jobs and notifications | Supporting/generic |

## Consistency Model

- One inventory command creates one atomic `inventory_transaction` with balanced
  entries.
- Lot balance cannot become negative.
- Cross-context effects use transactional outbox events and idempotent handlers.
- Cost and reporting snapshots are eventually updated and carry generation status.
- Every tenant-owned transaction sets a tenant context used by RLS.

## Security

- Local password/session authentication with optional local TOTP.
- Scoped roles at tenant and branch level.
- Backend application use cases make final authorization decisions.
- PostgreSQL RLS adds isolation defense in depth.
- Protected commands commit audit evidence with the business result.

## Operational Simplicity

- No microservices, message broker, cache cluster or analytics warehouse in V1.
- No payment, identity, email, POS or supplier integration.
- PostgreSQL jobs handle bounded asynchronous work.
- Deployment and migration changes remain backward compatible within rollback window.

## Review Triggers

An ADR is required before introducing external APIs, real-money workflows, deeper
recipe recursion, a dedicated broker/store, cross-context table writes or a separate
service deployment.
