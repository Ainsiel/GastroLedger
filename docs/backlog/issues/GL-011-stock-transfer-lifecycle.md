---
id: GL-011
title: Complete a stock transfer lifecycle
status: draft
readiness: blocked
primary_context: Inventory & Production
labels: [gridwork, type:feature, slice:vertical]
dependencies: [GL-009]
requirements: [FR-016, FR-020, FR-027]
use_cases: [UC-015, UC-016, UC-017]
test_cases: [TC-015-S, TC-015-A, TC-015-F, TC-016-S, TC-016-A, TC-016-F, TC-017-S, TC-017-A, TC-017-F, IT-012, IT-013]
quality_attributes: [QA-002, QA-010, QA-011]
---

# Goal

Operators can request, approve, dispatch and receive a stock transfer while
preserving lot lineage and reconciling dispatched, received and loss quantities.

## Scope

- Frontend: role-sensitive transfer lifecycle under `(app)/inventory`.
- API: request, approval, dispatch and receipt contracts.
- Domain/application: different warehouses, approval, FEFO dispatch, partial
  quantities, in-transit state, loss and duplicate-receipt policy.
- Persistence: transfer/line lifecycle plus immutable inventory transactions.
- Tests: state transitions, races, partials, lineage and duplicate receipt.

## Exclusions

- External logistics integration, autonomous transfer creation and stock edits.

## Acceptance Criteria

- [ ] A valid request is approved with requested and approved quantities preserved.
- [ ] Dispatch cannot exceed approval or available stock and creates in-transit
  evidence.
- [ ] Receipt creates destination stock with source-lot lineage.
- [ ] Received plus transport loss never exceeds dispatched quantity.
- [ ] Invalid, duplicate and racing transitions commit one valid result at most.

## Definition Of Done

- [ ] All TC-015/016/017 flows and IT-012/013 pass.
- [ ] Transfer approvals and variances are audited.
- [ ] Frontend exposes pending, partial, conflict and completed states.
- [ ] Required root quality commands and `regression-gate` pass.
