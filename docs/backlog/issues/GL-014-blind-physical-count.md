---
id: GL-014
title: Perform a blind count and reconcile variance
status: draft
readiness: blocked
primary_context: Inventory & Production
labels: [gridwork, type:feature, slice:vertical, mode:afk, agent:implementer, workflow:tdd-implementation]
dependencies: [GL-002, GL-009]
requirements: [FR-019, FR-020, FR-027]
use_cases: [UC-020]
test_cases: [TC-020-S, TC-020-A, TC-020-F, IT-015]
quality_attributes: [QA-002, QA-010, QA-011]
---

# Goal

A counter can submit a blind physical count and a separate authorized reviewer can
approve reasoned variance movements.

## Scope

- Frontend: blind entry, recount, review and approval states.
- API: create, submit, request-recount and approve contracts.
- Domain/application: hidden theoretical balance, threshold and separation-of-duty
  policy.
- Persistence: count lifecycle, lines, approval and variance transaction.
- Tests: approved variance, recount threshold and self-approval denial.

## Exclusions

- Unreviewed stock edits and exposing theoretical balance to the counter.

## Acceptance Criteria

- [ ] The counter cannot view theoretical stock during blind entry.
- [ ] Approved reviewed variance posts one immutable adjustment transaction.
- [ ] Large variance requires recount before adjustment.
- [ ] The counter cannot approve their own count.

## Definition Of Done

- [ ] TC-020-S/A/F and IT-015 pass.
- [ ] Approval and denial evidence are audited.
- [ ] Critical workflow has keyboard/accessibility E2E coverage.
- [ ] Required root quality commands and `regression-gate` pass.
