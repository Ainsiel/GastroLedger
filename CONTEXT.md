# GastroLedger Agent Context

Compact context for agents working in this repository. Approved product and technical
truth lives under `docs/`; repository code and configuration are the truth for what is
currently implemented and executable.

## Purpose

GastroLedger is a multi-tenant operational SaaS for restaurant groups, chains and
franchises. Its goal is to connect recipes, purchasing, lot-aware inventory,
production, store operations and profitability analysis so operators can explain
consumption, waste, cost and variance.

## Scope And Exclusions

Approved V1 capabilities:

- tenant, local user, role, branch and warehouse administration;
- units, ingredients, versioned recipes, yields and theoretical cost;
- suppliers, purchase suggestions, orders, receipts and operational returns;
- immutable lot-aware inventory, production, transfers, waste, expiry and counts;
- simulated/manual/CSV sales consumption, operational cash records and workforce
  records;
- non-financial royalty estimates, ordering holds, audit and profitability reports.

Permanent exclusions:

- no external APIs, external SaaS providers or external network adapters;
- no POS, identity, email, SMS, banking or supplier integration;
- no real payments, paid subscriptions, settlements, collections or money transfers;
- no accounting, tax documents, formal invoicing or payroll calculation;
- no negative stock as normal operation and no arbitrary recipe recursion;
- no microservices, broker, Redis, cache cluster or analytics warehouse in V1.

Financial-looking values are informational operational evidence only. Any external
integration or real-money lifecycle requires SDD expansion, security review and a new
ADR.

## Architecture

- Modular monolith in one monorepo.
- Next.js App Router frontend in `apps/web`.
- FastAPI API and backend modules in `apps/api`.
- Separate worker entry point in `apps/worker`; it reuses public API composition and
  modules instead of duplicating domain code.
- PostgreSQL is the planned transactional truth for tenant isolation, jobs, outbox
  and projections.
- `packages/api-contract` contains transport contracts only.
- Runtime flow: browser -> Next.js -> FastAPI -> bounded contexts -> PostgreSQL.
- Async flow: worker -> PostgreSQL jobs/outbox -> application use cases.
- No runtime flow requires an external API.

The current repository is an architecture foundation, not a functional product.
Shared-schema RLS, functional tables, business rules and product use cases remain to
be implemented through approved TDD work orders.

## Bounded Contexts

| Context | Owns |
|---|---|
| Platform & Organization | Tenant, local identity, session, role, branch and warehouse scope |
| Menu Engineering | Units, ingredients, recipe versions, yields and cost snapshots |
| Procurement | Suppliers, offers, purchase orders, receipts and returns |
| Inventory & Production | Lots, immutable ledger, allocation, production, transfers, waste and counts |
| Store Operations | Operational sales imports, cash shifts, schedules and attendance |
| Control & Insights | Royalty estimates, holds, audit, jobs, notifications and projections |

Cross-context interaction uses published application contracts or outbox events.
Contexts never write another context's mutable tables.

## Main ADR Decisions

The ADR files currently have documentary status `proposed` and are the accepted
design direction for the foundation:

1. `ADR-0001`: modular monolith with Next.js, FastAPI API/worker and PostgreSQL.
2. `ADR-0002`: shared-schema multi-tenancy with mandatory `tenant_id` and RLS.
3. `ADR-0003`: immutable, lot-aware inventory ledger; FEFO then FIFO; no negative
   balances.
4. `ADR-0004`: immutable approved recipe versions and historical cost snapshots.
5. `ADR-0005`: no external APIs or real-money workflows in V1.
6. `ADR-0006`: PostgreSQL leased jobs and transactional outbox, with no broker.

## Dependency Rules

1. Domain policy imports no FastAPI, Next.js, PostgreSQL or transport schemas.
2. Application interactors orchestrate domain policy, authorization, transactions
   and owned ports.
3. FastAPI routers map transport only and call application public APIs.
4. PostgreSQL adapters implement repositories owned by one bounded context.
5. Next.js owns presentation and interaction state; FastAPI owns authorization and
   business truth.
6. Contexts depend only on another context's public contract or outbox event.
7. Shared code contains technical primitives, never business behavior.
8. Tenant context is mandatory before tenant-owned repository operations.
9. Frontend features do not import another feature's internals.
10. No external HTTP client dependency is allowed without an approved ADR.

## Branch Model

- `main`: production.
- `develop`: integration.
- `feature/<work-order-id>-<slug>`: one approved work order, created from and
  targeting `develop`.
- Release PRs go from `develop` to `main`.
- Direct pushes to `develop` and `main` are forbidden.
- Feature PRs use squash merge; release PRs use merge commits.
- Required order: local checks -> commit -> push -> PR -> CI -> verifier -> merge.
- Branch creation, stage, commit, push, PR, merge, production approval and rollback
  remain separate human gates.

## Gridwork Workflows

Use the orchestrator contract in `.gridwork/agents/orchestrator/PROMPT.md`. Available
workflows are:

- Discovery/design: `intake-existing-code`, `ideation-from-zero`,
  `architecture-ddd`.
- Foundations: `repository-bootstrap`, `architecture-foundation`,
  `delivery-infrastructure`.
- Delivery: `backlog-management`, `backlog-task-delivery`,
  `tdd-implementation`, `verification-pr`, `feature-pr-delivery`.
- Operations: `ci-failure-repair`, `release-promotion`.

Functional implementation starts only from approved vertical work orders. Do not
use skills or create HTML artifacts for GastroLedger work.

## Important Paths

| Path | Purpose |
|---|---|
| `docs/product/` | Product purpose, scope and accepted product decisions |
| `docs/sdd/` | Requirements, use cases, tests and traceability |
| `docs/architecture/` | Approved architecture, ADRs and operational plans |
| `apps/web/app/` | Next.js App Router route groups |
| `apps/web/features/` | Public frontend feature boundaries |
| `apps/api/gastroledger_api/modules/` | Backend bounded-context boundaries |
| `apps/api/gastroledger_api/application/` | Shared application contracts and ports |
| `apps/api/gastroledger_api/composition.py` | Backend composition root |
| `apps/worker/` | Separate technical worker entry point |
| `packages/api-contract/` | Transport-only TypeScript contracts |
| `tests/architecture/` | Backend/frontend dependency conformance |
| `tests/infrastructure/` | Compose and GitHub Actions contract checks |
| `tests/integration/` | PostgreSQL and runtime boundary harnesses |
| `tests/e2e/` | Critical technical smoke; no functional E2E yet |
| `infra/compose/` | Base Compose contract and environment overlays |
| `infra/containers/` | Container build definitions |
| `infra/migrations/` | Migration chain; currently technical foundation only |
| `.github/workflows/` | Reusable and branch-specific CI contracts |
| `.gridwork/` | Gridwork agents, workflows and policies |

## Confirmed Commands

Commands are defined by the root `package.json` or the checked-in Compose contracts.
They were confirmed on 2026-06-14.

```text
npm run bootstrap
npm run lint
npm test
npm run test:migrations
npm run build
npm run compose:config
npm run compose:config:qa
npm run compose:config:production-like
npm run compose:config:integration
```

Environment startup, shutdown and critical-smoke commands are documented and tested
in `README.md`.

## Test Strategy

- Unit: frontend components/contracts and future pure domain policy.
- Architecture: forbidden imports, public module boundaries and framework isolation.
- Infrastructure: Compose/GitHub Actions contracts, permissions and exclusions.
- Integration: real isolated PostgreSQL, transactions and tenant-context harness.
- Contract: transport compatibility between FastAPI and Next.js consumers.
- E2E: a small set of critical visible workflows; currently only technical health
  smoke exists.
- Performance: added only from an accepted measured baseline.

CI contracts:

- `feature/* -> develop`: `feature / regression-gate`.
- Push to `develop`: `develop / integration-gate`.
- `develop -> main`: `release / full-regression-gate`.
- Push to `main`: `production / smoke-gate`, which performs no deployment.

## Current State

As of 2026-06-14:

- branch model and delivery workflows exist; `develop` is the active integration
  branch and `main` represents production;
- repository bootstrap, architecture foundation and delivery infrastructure are
  materialized;
- web, API and worker expose technical health checks;
- six backend module boundaries, frontend feature/route boundaries, application
  contracts, ports, errors, tenant context and composition root exist;
- Compose supports develop, QA, production-like and isolated integration overlays;
- GitHub Actions provide reusable frontend/backend/integration checks;
- the PostgreSQL migration chain contains only a technical foundation check;
- no functional use case, product table, RLS policy, external client or financial
  transaction behavior is implemented.

Before changing behavior, read the relevant `docs/sdd/`, `docs/architecture/`,
context public contract and tests. Preserve the modular monolith and add behavior
only through an approved TDD work order.
