---
id: GL-008
title: Recalculate recipe cost snapshots asynchronously
status: draft
readiness: blocked
primary_context: Menu Engineering
labels: [gridwork, type:feature, slice:vertical]
dependencies: [GL-007]
requirements: [FR-010, FR-031]
use_cases: [UC-010]
test_cases: [TC-010-S, TC-010-A, TC-010-F, IT-003, IT-018, IT-019, IT-020]
quality_attributes: [QA-003, QA-007, QA-012, QA-013]
---

# Goal

Accepted cost or yield changes produce idempotent background recalculation and
publish new recipe cost snapshots while retaining visible failure/stale status.

## Scope

- Frontend: visible current, stale, pending and failed snapshot status.
- API/worker: projection request/status contracts and worker consumer.
- Domain/application: affected-recipe selection and reproducible snapshot policy.
- Persistence: PostgreSQL jobs, transactional outbox and cost snapshot status.
- Tests: lease/retry, outbox atomicity, repeated events and failure retention.

## Exclusions

- External brokers, Redis, external notifications and rewriting historical snapshots.

## Acceptance Criteria

- [ ] An accepted cost-impacting change commits its outbox fact atomically.
- [ ] Repeated facts coalesce or produce one idempotent latest snapshot.
- [ ] A worker failure retains the prior snapshot and actionable retry evidence.
- [ ] Successful affected snapshots update within the approved five-minute target.

## Definition Of Done

- [ ] TC-010-S/A/F and IT-003/018/019/020 pass.
- [ ] Worker jobs carry tenant context and expose correlation evidence.
- [ ] No broker or external service is introduced.
- [ ] Required root quality commands and `regression-gate` pass.
