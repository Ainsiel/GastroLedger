---
id: GL-021
title: Calculate non-financial royalty estimates
status: draft
readiness: blocked
primary_context: Control & Insights
labels: [gridwork, type:feature, slice:vertical, mode:afk, agent:implementer, workflow:tdd-implementation]
dependencies: [GL-008, GL-015]
requirements: [FR-025]
use_cases: [UC-024-S]
test_cases: [TC-024-S]
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

## Definition Of Done

- [ ] TC-024-S and the missing-policy portion of TC-024-F pass.
- [ ] Source facts are consumed without mutating Store Operations.
- [ ] No invoice, debt or collection behavior is introduced.
- [ ] Required root quality commands and `regression-gate` pass.
