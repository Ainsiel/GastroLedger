---
id: GL-022
title: Analyze cost variance and menu profitability
status: draft
readiness: blocked
primary_context: Control & Insights
labels: [gridwork, type:feature, slice:vertical]
dependencies: [GL-014, GL-015]
requirements: [FR-026]
use_cases: [UC-025]
test_cases: [TC-025-S, TC-025-A, TC-025-F, IT-024]
quality_attributes: [QA-003, QA-005, QA-011, QA-012]
---

# Goal

An analyst can compare theoretical consumption, actual inventory movement and menu
profitability by branch and period, with incomplete confidence made explicit.

## Scope

- Frontend: filterable report with loading, complete and incomplete states.
- API/worker: report query and projection-status contracts.
- Domain/application: trusted-fact reconciliation and confidence/incomplete policy.
- Persistence: report projections and source references.
- Tests: reconciled report, filters and open-import/incomplete inputs.

## Exclusions

- External analytics warehouse, accounting statements and guessed final figures.

## Acceptance Criteria

- [ ] Closed trusted inputs produce theoretical, actual and profitability metrics.
- [ ] Branch/category/period filters preserve consistent totals.
- [ ] Open imports or incomplete snapshots mark the report incomplete with reasons.
- [ ] The report never mutates source business facts.

## Frontend Delivery Contract

- Follow `docs/backlog/frontend-delivery-contract.md`, `docs/architecture/frontend/ui-design-spec.md`, `docs/architecture/frontend/frontend-architecture.md` and ADR-0007.
- Implement the owned App Router route with the approved `(app)` shell, existing GastroLedger design tokens and shadcn/ui-derived primitives; add shared primitives only for confirmed consumers.
- Define and test every applicable loading, empty, validation/error, unauthorized, success, stale/conflict and destructive state without enabling unimplemented behavior.
- Verify keyboard/focus/accessibility behavior and responsive rendering at 390, 1024 and 1440 CSS pixels with no horizontal scroll at 390.
- Record component or feature tests, integrated route evidence and visual QA evidence. No external UI assets, APIs or services are allowed.
## Definition Of Done

- [ ] TC-025-S/A/F and IT-024 pass.
- [ ] Critical report states meet accessibility expectations.
- [ ] Query performance has a recorded baseline before adding indexes.
- [ ] Required root quality commands and `regression-gate` pass.
