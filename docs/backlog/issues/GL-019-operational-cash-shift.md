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

## Frontend Delivery Contract

- Follow `docs/backlog/frontend-delivery-contract.md`, `docs/architecture/frontend/ui-design-spec.md`, `docs/architecture/frontend/frontend-architecture.md` and ADR-0007.
- Implement the owned App Router route with the approved `(app)` shell, existing GastroLedger design tokens and shadcn/ui-derived primitives; add shared primitives only for confirmed consumers.
- Define and test every applicable loading, empty, validation/error, unauthorized, success, stale/conflict and destructive state without enabling unimplemented behavior.
- Verify keyboard/focus/accessibility behavior and responsive rendering at 390, 1024 and 1440 CSS pixels with no horizontal scroll at 390.
- Record component or feature tests, integrated route evidence and visual QA evidence. No external UI assets, APIs or services are allowed.
## Definition Of Done

- [ ] TC-022-S/A/F and IT-022 pass.
- [ ] Review and corrections are audited.
- [ ] No real-money transaction capability is introduced.
- [ ] Required root quality commands and `regression-gate` pass.
