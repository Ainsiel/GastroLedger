---
id: GL-010
title: Post a production batch and prepared lot
status: done
readiness: done
primary_context: Inventory & Production
labels: [gridwork, type:feature, slice:vertical]
dependencies: [GL-006, GL-009]
pull_request: https://github.com/Ainsiel/GastroLedger/pull/34
merged_at: 2026-06-20T17:06:43Z
merge_commit: 647cce4918f4e91e6ea35772a9249acfb84b58b7
requirements: [FR-015, FR-020, FR-031]
use_cases: [UC-011]
test_cases: [TC-011-S, TC-011-A, TC-011-F, IT-011]
quality_attributes: [QA-002, QA-010, QA-012]
---

# Goal

A production lead can post a batch that consumes approved-recipe inputs and creates
a traceable prepared lot in one atomic inventory transaction.

## Scope

- Frontend: production batch entry and visible yield/shortage states.
- API: batch posting command/result contract.
- Domain/application: approved recipe reference, FEFO/FIFO input allocation, actual
  yield and variance reason.
- Persistence: production batch, input entries, output lot and immutable ledger.
- Tests: atomic success, yield variance and insufficient-stock rollback.

## Exclusions

- Editing recipe versions, negative stock and arbitrary recipe recursion.

## Acceptance Criteria

- [ ] Sufficient FEFO inputs decrease and one prepared lot increases atomically.
- [ ] Lower actual yield records a reasoned production variance.
- [ ] Insufficient stock or inactive recipe commits no input, output or batch.
- [ ] The batch references the exact immutable approved recipe version.

## Frontend Delivery Contract

- Follow `docs/backlog/frontend-delivery-contract.md`, `docs/architecture/frontend/ui-design-spec.md`, `docs/architecture/frontend/frontend-architecture.md` and ADR-0007.
- Implement the owned App Router route with the approved `(app)` shell, existing GastroLedger design tokens and shadcn/ui-derived primitives; add shared primitives only for confirmed consumers.
- Define and test every applicable loading, empty, validation/error, unauthorized, success, stale/conflict and destructive state without enabling unimplemented behavior.
- Verify keyboard/focus/accessibility behavior and responsive rendering at 390, 1024 and 1440 CSS pixels with no horizontal scroll at 390.
- Record component or feature tests, integrated route evidence and visual QA evidence. No external UI assets, APIs or services are allowed.
## Definition Of Done

- [ ] TC-011-S/A/F and IT-011 pass.
- [ ] Inventory entries remain immutable and balances cannot become negative.
- [ ] Visible correlation and failure states are covered.
- [ ] Required root quality commands and `regression-gate` pass.
