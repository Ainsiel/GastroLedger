---
id: GL-019
title: Reconcile an operational cash shift
status: draft
readiness: blocked
primary_context: Store Operations
labels: [gridwork, type:feature, slice:vertical]
dependencies: [GL-002, GL-003]
requirements: [FR-023, FR-027]
use_cases: [UC-022]
test_cases: [TC-022-S, TC-022-A, TC-022-F, IT-022]
quality_attributes: [QA-009, QA-010, QA-011]
---

# Goal

A cashier can open and close an operational cash shift, and a manager can review a
reasoned variance without processing or settling money.

## Scope

- Frontend: opening float, closing denomination count and variance explanation.
- API: open, close and review contracts.
- Domain/application: one open shift per cashier/branch and review threshold.
- Persistence: operational cash shift lifecycle and audit evidence.
- Tests: close variance, manager explanation and duplicate/wrong-cashier failure.

## Exclusions

- Payments, settlement, banking, accounting entries and cash transfer.

## Acceptance Criteria

- [ ] Opening and closing records produce an informational operational variance.
- [ ] Variance above threshold retains manager explanation and review.
- [ ] Duplicate open shift and closing another cashier's shift are rejected.
- [ ] UI and contracts never describe the result as payment or settlement truth.

## Definition Of Done

- [ ] TC-022-S/A/F and IT-022 pass.
- [ ] Review and corrections are audited.
- [ ] No real-money transaction capability is introduced.
- [ ] Required root quality commands and `regression-gate` pass.
