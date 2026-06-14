---
id: GL-012
title: Record operational waste with approval evidence
status: draft
readiness: blocked
primary_context: Inventory & Production
labels: [gridwork, type:feature, slice:vertical, mode:afk, agent:implementer, workflow:tdd-implementation]
dependencies: [GL-009]
requirements: [FR-017, FR-020, FR-027]
use_cases: [UC-018]
test_cases: [TC-018-S, TC-018-A, TC-018-F, IT-014]
quality_attributes: [QA-002, QA-010, QA-011]
---

# Goal

An authorized operator can record reasoned operational waste against an available
lot, with approval required before high-value waste posts.

## Scope

- Frontend: waste entry, approval-pending and posted states.
- API: submit, approve and reject contracts.
- Domain/application: reason, permission, quantity and approval threshold policy.
- Persistence: waste record, approval evidence and immutable inventory transaction.
- Tests: normal post, approval gate, forbidden and excessive quantity.

## Exclusions

- Accounting write-offs, supplier returns and editing posted movements.

## Acceptance Criteria

- [ ] Valid authorized waste decreases the selected lot and records audit evidence.
- [ ] High-value waste creates no movement until separate approval.
- [ ] Missing reason, forbidden actor or excessive quantity creates no movement.
- [ ] Posted waste is corrected only through a compensating transaction.

## Definition Of Done

- [ ] TC-018-S/A/F and IT-014 pass.
- [ ] Approval separation and audit atomicity are proven.
- [ ] Frontend preserves input after recoverable rejection.
- [ ] Required root quality commands and `regression-gate` pass.
