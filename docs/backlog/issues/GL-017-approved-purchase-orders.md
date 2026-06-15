---
id: GL-017
title: Create approved purchase orders
status: draft
readiness: blocked
primary_context: Procurement
labels: [gridwork, type:feature, slice:vertical]
dependencies: [GL-009, GL-016]
requirements: [FR-012, FR-027]
use_cases: [UC-012]
test_cases: [TC-012-S, TC-012-A, TC-012-F, IT-021]
quality_attributes: [QA-009, QA-010, QA-011]
---

# Goal

A purchasing manager can review suggestions or selected offers and create an
approved purchase order when authorization and ordering-hold policy allow it.

## Scope

- Frontend: suggestion review, editable quantities and approval states.
- API: purchase-order draft/approval contracts.
- Domain/application: reorder suggestion, positive quantity, offer validity,
  authorization and ordering hold decision.
- Persistence: purchase orders, lines and approval audit evidence.
- Tests: accepted approval, edited suggestion and hold/forbidden failures.

## Exclusions

- Autonomous commitments, supplier API submission, payments and accounting.

## Acceptance Criteria

- [ ] Authorized approval creates an order from valid selected offers.
- [ ] Current stock policy and supplier offers can produce an editable reorder
  suggestion.
- [ ] Edited suggestions produce only reviewed quantities.
- [ ] Invalid quantity, active hold and forbidden approver create no order.
- [ ] Approved order retains source offer and actor evidence.

## Frontend Delivery Contract

- Follow `docs/backlog/frontend-delivery-contract.md`, `docs/architecture/frontend/ui-design-spec.md`, `docs/architecture/frontend/frontend-architecture.md` and ADR-0007.
- Implement the owned App Router route with the approved `(app)` shell, existing GastroLedger design tokens and shadcn/ui-derived primitives; add shared primitives only for confirmed consumers.
- Define and test every applicable loading, empty, validation/error, unauthorized, success, stale/conflict and destructive state without enabling unimplemented behavior.
- Verify keyboard/focus/accessibility behavior and responsive rendering at 390, 1024 and 1440 CSS pixels with no horizontal scroll at 390.
- Record component or feature tests, integrated route evidence and visual QA evidence. No external UI assets, APIs or services are allowed.
## Definition Of Done

- [ ] TC-012-S/A/F and IT-021 pass.
- [ ] Procurement consumes ordering hold only through its public contract.
- [ ] UI clearly distinguishes suggestion from approved order.
- [ ] Required root quality commands and `regression-gate` pass.
