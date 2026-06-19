---
id: GL-007
title: Approve menu items and branch margin
status: in_pr
readiness: ready
primary_context: Menu Engineering
labels: [gridwork, type:feature, slice:vertical, status:in-pr]
dependencies: [GL-006]
pull_request: https://github.com/Ainsiel/GastroLedger/pull/31
requirements: [FR-008, FR-009, FR-031]
use_cases: [UC-009]
test_cases: [TC-009-S, TC-009-A, TC-009-F]
quality_attributes: [QA-003, QA-011, QA-012]
---

# Goal

A chef or analyst can approve a menu-item recipe and see its theoretical cost,
branch contribution margin and suggested informational price.

## Scope

- Frontend: menu-item editor, approval and branch margin view.
- API: menu recipe, branch price and margin result contracts.
- Domain/application: component validation, snapshot use and approval completeness.
- Persistence: menu recipe versions and effective-dated branch prices.
- Tests: approval, branch override and missing-cost states.

## Exclusions

- Payment processing, price synchronization, tax calculation and sales import.

## Acceptance Criteria

- [ ] Costed components produce theoretical cost, contribution margin and suggested
  informational price.
- [ ] A branch price override changes margin without mutating the recipe.
- [ ] Missing active component cost blocks approval and explains every gap.
- [ ] Approved menu versions remain immutable and reference exact components.

## Frontend Delivery Contract

- Follow `docs/backlog/frontend-delivery-contract.md`, `docs/architecture/frontend/ui-design-spec.md`, `docs/architecture/frontend/frontend-architecture.md` and ADR-0007.
- Implement the owned App Router route with the approved `(app)` shell, existing GastroLedger design tokens and shadcn/ui-derived primitives; add shared primitives only for confirmed consumers.
- Define and test every applicable loading, empty, validation/error, unauthorized, success, stale/conflict and destructive state without enabling unimplemented behavior.
- Verify keyboard/focus/accessibility behavior and responsive rendering at 390, 1024 and 1440 CSS pixels with no horizontal scroll at 390.
- Record component or feature tests, integrated route evidence and visual QA evidence. No external UI assets, APIs or services are allowed.
## Definition Of Done

- [ ] TC-009-S/A/F pass.
- [ ] Visible stale/missing/conflict states are covered.
- [ ] Amounts remain informational and no financial transaction is created.
- [ ] Required root quality commands and `regression-gate` pass.
