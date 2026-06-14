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

## Definition Of Done

- [ ] TC-025-S/A/F and IT-024 pass.
- [ ] Critical report states meet accessibility expectations.
- [ ] Query performance has a recorded baseline before adding indexes.
- [ ] Required root quality commands and `regression-gate` pass.
