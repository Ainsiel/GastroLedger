---
id: GL-018
title: Record supplier return and expected adjustment
status: draft
readiness: blocked
primary_context: Procurement
labels: [gridwork, type:feature, slice:vertical]
dependencies: [GL-009]
requirements: [FR-014, FR-020, FR-027]
use_cases: [UC-014]
test_cases: [TC-014-S, TC-014-A, TC-014-F]
quality_attributes: [QA-002, QA-010, QA-011]
---

# Goal

A warehouse operator can return available quantity from an accepted receipt lot,
decrease stock and record an expected non-financial supplier adjustment.

## Scope

- Frontend: return entry and visible remaining-lot state.
- API: supplier-return posting contract and accepted-return event.
- Domain/application: accepted-receipt reference, available quantity and supplier
  status policy.
- Persistence: return/line records plus immutable inventory transaction.
- Tests: full/partial return, excessive quantity and closed supplier.

## Exclusions

- Credit notes, refunds, supplier payments and accounting postings.

## Acceptance Criteria

- [ ] A valid return decreases the received lot and records expected adjustment.
- [ ] A partial return preserves the remaining available balance.
- [ ] Excessive quantity or closed supplier produces no movement.
- [ ] Expected adjustment language remains explicitly non-financial.

## Frontend Delivery Contract

- Follow `docs/backlog/frontend-delivery-contract.md`, `docs/architecture/frontend/ui-design-spec.md`, `docs/architecture/frontend/frontend-architecture.md` and ADR-0007.
- Implement the owned App Router route with the approved `(app)` shell, existing GastroLedger design tokens and shadcn/ui-derived primitives; add shared primitives only for confirmed consumers.
- Define and test every applicable loading, empty, validation/error, unauthorized, success, stale/conflict and destructive state without enabling unimplemented behavior.
- Verify keyboard/focus/accessibility behavior and responsive rendering at 390, 1024 and 1440 CSS pixels with no horizontal scroll at 390.
- Record component or feature tests, integrated route evidence and visual QA evidence. No external UI assets, APIs or services are allowed.
## Definition Of Done

- [ ] TC-014-S/A/F pass with real PostgreSQL.
- [ ] Return and inventory movement commit atomically through public contracts.
- [ ] Protected action audit evidence is retained.
- [ ] Required root quality commands and `regression-gate` pass.
