---
id: GL-015
title: Import sales and resolve allocation exceptions
status: draft
readiness: blocked
primary_context: Store Operations
labels: [gridwork, type:feature, slice:vertical]
dependencies: [GL-008, GL-009]
requirements: [FR-021, FR-022, FR-030, FR-020]
use_cases: [UC-021]
test_cases: [TC-021-S, TC-021-A, TC-021-F, IT-016, IT-017]
quality_attributes: [QA-002, QA-004, QA-006, QA-011, QA-013]
---

# Goal

A branch manager can preview and accept a bounded CSV or simulation; valid sale
lines consume approved recipes once and shortage lines become actionable exceptions.

## Scope

- Frontend: upload/simulation preview, validation, pending, partial and exception
  states.
- API/worker: bounded import, idempotency, status and accepted-sale event contracts.
- Domain/application: row validation, active menu reference, partial-result policy
  and inventory allocation orchestration.
- Persistence: sales imports/records/lines and allocation exceptions.
- Tests: duplicate key, mixed valid/shortage input, FEFO consumption and bounded
  import behavior.

## Exclusions

- POS integration, payments, negative stock and external file storage.

## Acceptance Criteria

- [ ] A valid accepted import consumes approved recipe components by FEFO exactly
  once.
- [ ] Mixed input commits valid lines and creates explicit shortage exceptions.
- [ ] Duplicate key, unknown item and invalid period reject affected input without
  duplicate sales or movements.
- [ ] Preview and exports are safe for CSV content and require no Internet.

## Frontend Delivery Contract

- Follow `docs/backlog/frontend-delivery-contract.md`, `docs/architecture/frontend/ui-design-spec.md`, `docs/architecture/frontend/frontend-architecture.md` and ADR-0007.
- Implement the owned App Router route with the approved `(app)` shell, existing GastroLedger design tokens and shadcn/ui-derived primitives; add shared primitives only for confirmed consumers.
- Define and test every applicable loading, empty, validation/error, unauthorized, success, stale/conflict and destructive state without enabling unimplemented behavior.
- Verify keyboard/focus/accessibility behavior and responsive rendering at 390, 1024 and 1440 CSS pixels with no horizontal scroll at 390.
- Record component or feature tests, integrated route evidence and visual QA evidence. No external UI assets, APIs or services are allowed.
## Definition Of Done

- [ ] TC-021-S/A/F and IT-016/017 pass.
- [ ] Import status and incomplete results are visible with correlation IDs.
- [ ] The worker uses tenant context and idempotent public contracts.
- [ ] Required root quality commands and `regression-gate` pass.
