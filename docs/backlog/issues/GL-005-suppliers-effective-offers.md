---
id: GL-005
title: Manage suppliers and effective-dated offers
status: draft
readiness: blocked
primary_context: Procurement
labels: [gridwork, type:feature, slice:vertical]
dependencies: [GL-004]
requirements: [FR-011]
use_cases: [UC-007]
test_cases: [TC-007-S, TC-007-A, TC-007-F]
quality_attributes: [QA-001, QA-011, QA-012]
---

# Goal

A purchasing manager can maintain tenant-scoped suppliers and effective-dated
ingredient offers with visible price history.

## Scope

- Frontend: supplier and offer workflow under `(app)/procurement`.
- API: supplier and offer lifecycle contracts.
- Domain/application: tenant scope, compatible purchase unit and non-overlapping
  validity.
- Persistence: supplier and offer history relations.
- Tests: active/future offer selection, overlap and cross-tenant rejection.

## Exclusions

- External supplier APIs, purchase orders, payments and accounting entries.

## Acceptance Criteria

- [ ] A valid offer links one tenant supplier, ingredient, purchase unit, price and
  validity.
- [ ] Future offers preserve the current active offer until effective.
- [ ] Overlap and cross-tenant references are rejected without changes.
- [ ] Price history remains visible and immutable as operational evidence.

## Frontend Delivery Contract

- Follow `docs/backlog/frontend-delivery-contract.md`, `docs/architecture/frontend/ui-design-spec.md`, `docs/architecture/frontend/frontend-architecture.md` and ADR-0007.
- Implement the owned App Router route with the approved `(app)` shell, existing GastroLedger design tokens and shadcn/ui-derived primitives; add shared primitives only for confirmed consumers.
- Define and test every applicable loading, empty, validation/error, unauthorized, success, stale/conflict and destructive state without enabling unimplemented behavior.
- Verify keyboard/focus/accessibility behavior and responsive rendering at 390, 1024 and 1440 CSS pixels with no horizontal scroll at 390.
- Record component or feature tests, integrated route evidence and visual QA evidence. No external UI assets, APIs or services are allowed.
## Definition Of Done

- [ ] TC-007-S/A/F pass.
- [ ] Informational amounts cannot be mistaken for payment truth.
- [ ] Procurement consumes ingredient identity through an approved contract.
- [ ] Required root quality commands and `regression-gate` pass.
