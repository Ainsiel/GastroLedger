---
id: GL-001
title: Register a tenant and prove isolation
status: done
readiness: done
primary_context: Platform & Organization
labels: [gridwork, type:feature, slice:vertical]
dependencies: [repository-bootstrap, architecture-foundation, delivery-infrastructure]
requirements: [FR-001, FR-028]
use_cases: [UC-001]
test_cases: [TC-001-S, TC-001-A, TC-001-F, IT-001, IT-002]
quality_attributes: [QA-001, QA-009, QA-011, QA-013]
---

# Goal

A prospective administrator can register a company and receive a scoped local
session; another tenant's known identifiers remain inaccessible.

## Scope

- Frontend: accessible registration form and visible success, duplicate and
  validation states under `(public)/register`.
- API: typed registration command/result/error contract and authenticated tenant
  identity query.
- Domain/application: tenant registration aggregate, password/session policy,
  transaction and tenant context enforcement.
- Persistence: minimum Platform relations, production migration, mandatory
  `tenant_id`, RLS and hashed local session token.
- Tests: domain/application TDD, API contract, real PostgreSQL concurrency/RLS and
  critical registration E2E.

## Exclusions

- Invitations, role administration and optional TOTP.
- External identity, email, payments, subscriptions or external APIs.

## Acceptance Criteria

- [x] Unique company/admin data atomically creates tenant, settings, first admin
  membership and scoped session.
- [x] Optional first branch belongs only to the new tenant.
- [x] Duplicate company key or invalid credentials leaves no partial records.
- [x] Cross-tenant probes return no data and produce approved security evidence.
- [x] Registration and authenticated reads operate without Internet dependencies.

## Frontend Delivery Contract

- Follow `docs/backlog/frontend-delivery-contract.md`, `docs/architecture/frontend/ui-design-spec.md`, `docs/architecture/frontend/frontend-architecture.md` and ADR-0007.
- Implement the owned App Router route with the approved `(app)` shell, existing GastroLedger design tokens and shadcn/ui-derived primitives; add shared primitives only for confirmed consumers.
- Define and test every applicable loading, empty, validation/error, unauthorized, success, stale/conflict and destructive state without enabling unimplemented behavior.
- Verify keyboard/focus/accessibility behavior and responsive rendering at 390, 1024 and 1440 CSS pixels with no horizontal scroll at 390.
- Record component or feature tests, integrated route evidence and visual QA evidence. No external UI assets, APIs or services are allowed.
## Definition Of Done

- [x] Approved contracts, migration and RLS policies are implemented.
- [x] TC-001-S/A/F and IT-001/002 pass with real PostgreSQL.
- [x] Registration keyboard/accessibility states and API errors are covered.
- [x] Architecture tests, `npm run lint`, `npm test`, `npm run test:migrations` and
  `npm run build` pass.
- [x] No external client or real-money behavior is introduced.
