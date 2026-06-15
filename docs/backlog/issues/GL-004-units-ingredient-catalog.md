---
id: GL-004
title: Manage units and ingredient catalog
status: draft
readiness: blocked
primary_context: Menu Engineering
labels: [gridwork, type:feature, slice:vertical]
dependencies: [GL-003]
requirements: [FR-005, FR-006]
use_cases: [UC-005, UC-006]
test_cases: [TC-005-S, TC-005-A, TC-005-F, TC-006-S, TC-006-A, TC-006-F, IT-005]
quality_attributes: [QA-002, QA-011, QA-012]
---

# Goal

A menu engineer can create an ingredient whose purchase and consumption units use
validated, effective-dated conversion factors.

## Scope

- Frontend: unit/conversion and ingredient catalog workflows under `(app)/menu`.
- API: unit, conversion and ingredient lifecycle contracts.
- Domain/application: dimension compatibility, positive decimal factors, effective
  dates, unique codes and archive policy.
- Persistence: units, conversion factors, ingredients and branch policies.
- Tests: conversion precision, incompatible dimensions, overlap and archive
  behavior.

## Exclusions

- Recipes, supplier offers, inventory balances and float arithmetic.

## Acceptance Criteria

- [ ] Compatible units convert precise decimal quantities with a positive factor.
- [ ] Future factor versions do not replace the current factor early.
- [ ] Invalid dimensions, overlap and non-positive factors are rejected.
- [ ] A valid ingredient becomes available to downstream offers and recipes.
- [ ] Archiving preserves history and blocks new use.

## Frontend Delivery Contract

- Follow `docs/backlog/frontend-delivery-contract.md`, `docs/architecture/frontend/ui-design-spec.md`, `docs/architecture/frontend/frontend-architecture.md` and ADR-0007.
- Implement the owned App Router route with the approved `(app)` shell, existing GastroLedger design tokens and shadcn/ui-derived primitives; add shared primitives only for confirmed consumers.
- Define and test every applicable loading, empty, validation/error, unauthorized, success, stale/conflict and destructive state without enabling unimplemented behavior.
- Verify keyboard/focus/accessibility behavior and responsive rendering at 390, 1024 and 1440 CSS pixels with no horizontal scroll at 390.
- Record component or feature tests, integrated route evidence and visual QA evidence. No external UI assets, APIs or services are allowed.
## Definition Of Done

- [ ] TC-005-S/A/F, TC-006-S/A/F and IT-005 pass.
- [ ] API and frontend transport preserve decimal values.
- [ ] Menu Engineering does not import another context's internals.
- [ ] Required root quality commands and `regression-gate` pass.
