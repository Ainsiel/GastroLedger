---
id: GL-018
title: Record supplier return and expected adjustment
status: draft
readiness: blocked
primary_context: Procurement
labels: [gridwork, type:feature, slice:vertical, mode:afk, agent:implementer, workflow:tdd-implementation]
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

## Definition Of Done

- [ ] TC-014-S/A/F pass with real PostgreSQL.
- [ ] Return and inventory movement commit atomically through public contracts.
- [ ] Protected action audit evidence is retained.
- [ ] Required root quality commands and `regression-gate` pass.
