---
id: GL-021
title: Calculate non-financial royalty estimates
status: draft
readiness: blocked
primary_context: Control & Insights
labels: [gridwork, type:feature, slice:vertical]
dependencies: [GL-015]
requirements: [FR-025]
use_cases: [UC-024]
flows: [UC-024-S]
test_cases: [TC-024-S, TC-024-F]
quality_attributes: [QA-003, QA-010, QA-013]
---

# Goal

A franchise controller can calculate a reproducible, explicitly non-financial
royalty estimate from recorded operational sales and an effective policy.

## Scope

- Frontend: period estimate with policy/source explanation.
- API/worker: estimate request/status contracts.
- Domain/application: effective policy and reproducible percentage/rule calculation.
- Persistence: royalty policy and estimate snapshot.
- Tests: reproducible estimate, tenant scope and missing-policy failure inherited
  from UC-024.

## Exclusions

- Invoices, collections, debt automation, payments and accounting.

## Acceptance Criteria

- [ ] Recorded sales and an effective policy produce a reproducible period estimate.
- [ ] The estimate references source period and policy version.
- [ ] Missing policy produces no estimate and an actionable result.
- [ ] Every UI and API description states that the estimate is non-financial.

## Frontend Delivery Contract

- Follow `docs/backlog/frontend-delivery-contract.md`, `docs/architecture/frontend/ui-design-spec.md`, `docs/architecture/frontend/frontend-architecture.md` and ADR-0007.
- Implement the owned App Router route with the approved `(app)` shell, existing GastroLedger design tokens and shadcn/ui-derived primitives; add shared primitives only for confirmed consumers.
- Define and test every applicable loading, empty, validation/error, unauthorized, success, stale/conflict and destructive state without enabling unimplemented behavior.
- Verify keyboard/focus/accessibility behavior and responsive rendering at 390, 1024 and 1440 CSS pixels with no horizontal scroll at 390.
- Record component or feature tests, integrated route evidence and visual QA evidence. No external UI assets, APIs or services are allowed.
## Definition Of Done

- [ ] TC-024-S and the missing-policy portion of TC-024-F pass.
- [ ] Source facts are consumed without mutating Store Operations.
- [ ] No invoice, debt or collection behavior is introduced.
- [ ] Required root quality commands and `regression-gate` pass.
