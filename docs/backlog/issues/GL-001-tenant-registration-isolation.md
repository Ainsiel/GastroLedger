---
id: GL-001
title: Register a tenant and prove isolation
status: draft
readiness: ready
primary_context: Platform & Organization
labels: [gridwork, type:feature, slice:vertical, status:ready, mode:afk, agent:implementer, workflow:tdd-implementation]
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

- [ ] Unique company/admin data atomically creates tenant, settings, first admin
  membership and scoped session.
- [ ] Optional first branch belongs only to the new tenant.
- [ ] Duplicate company key or invalid credentials leaves no partial records.
- [ ] Cross-tenant probes return no data and produce approved security evidence.
- [ ] Registration and authenticated reads operate without Internet dependencies.

## Definition Of Done

- [ ] Approved contracts, migration and RLS policies are implemented.
- [ ] TC-001-S/A/F and IT-001/002 pass with real PostgreSQL.
- [ ] Registration keyboard/accessibility states and API errors are covered.
- [ ] Architecture tests, `npm run lint`, `npm test`, `npm run test:migrations` and
  `npm run build` pass.
- [ ] No external client or real-money behavior is introduced.
