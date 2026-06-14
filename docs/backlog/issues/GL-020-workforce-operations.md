---
id: GL-020
title: Plan shifts and record attendance
status: draft
readiness: blocked
primary_context: Store Operations
labels: [gridwork, type:feature, slice:vertical]
dependencies: [GL-002, GL-003]
requirements: [FR-024, FR-027]
use_cases: [UC-023]
test_cases: [TC-023-S, TC-023-A, TC-023-F, IT-023]
quality_attributes: [QA-009, QA-010, QA-011]
---

# Goal

A workforce coordinator can plan non-overlapping branch shifts and record
attendance that produces worked-hour, absence and overtime-candidate information.

## Scope

- Frontend: weekly schedule, attendance and exception approval.
- API: schedule, attendance and correction contracts.
- Domain/application: overlap, scoped correction and overtime-candidate policy.
- Persistence: work shifts, attendance and audited corrections.
- Tests: period report, approved exception, overlap and forbidden correction.

## Exclusions

- Payroll, salary calculation, payment and external workforce integrations.

## Acceptance Criteria

- [ ] Valid schedule and attendance produce worked-hour and absence information.
- [ ] An overtime candidate can be approved as an operational exception.
- [ ] Overlapping confirmed assignment and forbidden correction change nothing.
- [ ] Results are explicitly non-payroll records.

## Definition Of Done

- [ ] TC-023-S/A/F and IT-023 pass.
- [ ] Corrections retain actor and audit evidence.
- [ ] No payroll or salary calculation is introduced.
- [ ] Required root quality commands and `regression-gate` pass.
