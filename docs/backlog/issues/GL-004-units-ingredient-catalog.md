---
id: GL-004
title: Manage units and ingredient catalog
status: draft
readiness: blocked
primary_context: Menu Engineering
labels: [gridwork, type:feature, slice:vertical, mode:afk, agent:implementer, workflow:tdd-implementation]
dependencies: [GL-001, GL-003]
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

## Definition Of Done

- [ ] TC-005-S/A/F, TC-006-S/A/F and IT-005 pass.
- [ ] API and frontend transport preserve decimal values.
- [ ] Menu Engineering does not import another context's internals.
- [ ] Required root quality commands and `regression-gate` pass.
