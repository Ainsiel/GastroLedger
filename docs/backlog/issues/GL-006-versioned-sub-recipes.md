---
id: GL-006
title: Approve versioned sub-recipes
status: in_pr
readiness: in_pr
primary_context: Menu Engineering
labels: [gridwork, type:feature, slice:vertical]
dependencies: [GL-004]
requirements: [FR-007, FR-031]
use_cases: [UC-008]
test_cases: [TC-008-S, TC-008-A, TC-008-F, IT-006, IT-007]
quality_attributes: [QA-003, QA-011, QA-012]
---

# Goal

A chef can approve an immutable sub-recipe version with ingredients, expected yield
and a reproducible theoretical cost snapshot.

## Scope

- Frontend: sub-recipe editor, validation and approval states.
- API: draft, schedule and approval contracts.
- Domain/application: positive quantities/yield, unit compatibility, cycle and
  maximum-depth policy, immutable approval.
- Persistence: recipes, versions, components and initial cost snapshot.
- Tests: graph policy, concurrent approval and scheduled-version behavior.

## Exclusions

- Menu-item selling price, production posting and recursion beyond approved depth.

## Acceptance Criteria

- [ ] Valid ingredients, quantities and yield produce an approved immutable version
  and cost snapshot.
- [ ] A future version does not replace the active version early.
- [ ] Cycle, invalid yield, incompatible units and excessive depth are rejected.
- [ ] Concurrent approval yields one accepted immutable version.

## Frontend Delivery Contract

- Follow `docs/backlog/frontend-delivery-contract.md`, `docs/architecture/frontend/ui-design-spec.md`, `docs/architecture/frontend/frontend-architecture.md` and ADR-0007.
- Implement the owned App Router route with the approved `(app)` shell, existing GastroLedger design tokens and shadcn/ui-derived primitives; add shared primitives only for confirmed consumers.
- Define and test every applicable loading, empty, validation/error, unauthorized, success, stale/conflict and destructive state without enabling unimplemented behavior.
- Verify keyboard/focus/accessibility behavior and responsive rendering at 390, 1024 and 1440 CSS pixels with no horizontal scroll at 390.
- Record component or feature tests, integrated route evidence and visual QA evidence. No external UI assets, APIs or services are allowed.
## Definition Of Done

- [ ] TC-008-S/A/F and IT-006/007 pass.
- [ ] Frontend preserves draft input after recoverable errors.
- [ ] Historical approved versions cannot be edited.
- [ ] Required root quality commands and `regression-gate` pass.

## Delivery Evidence

Pull request: https://github.com/Ainsiel/GastroLedger/pull/30

Local TDD evidence recorded on 2026-06-19:

- Backend Menu Engineering unit tests passed.
- Frontend Menu Engineering feature tests passed.
- PostgreSQL recipe integration tests passed.
- `npm run lint` passed.
- Web and API contract builds passed.
- Visual QA was skipped by direct user instruction.
