---
id: GL-017
title: Create approved purchase orders
status: draft
readiness: blocked
primary_context: Procurement
labels: [gridwork, type:feature, slice:vertical, mode:afk, agent:implementer, workflow:tdd-implementation]
dependencies: [GL-005, GL-016]
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
- Domain/application: positive quantity, offer validity, authorization and ordering
  hold decision.
- Persistence: purchase orders, lines and approval audit evidence.
- Tests: accepted approval, edited suggestion and hold/forbidden failures.

## Exclusions

- Autonomous commitments, supplier API submission, payments and accounting.

## Acceptance Criteria

- [ ] Authorized approval creates an order from valid selected offers.
- [ ] Edited suggestions produce only reviewed quantities.
- [ ] Invalid quantity, active hold and forbidden approver create no order.
- [ ] Approved order retains source offer and actor evidence.

## Definition Of Done

- [ ] TC-012-S/A/F and IT-021 pass.
- [ ] Procurement consumes ordering hold only through its public contract.
- [ ] UI clearly distinguishes suggestion from approved order.
- [ ] Required root quality commands and `regression-gate` pass.
