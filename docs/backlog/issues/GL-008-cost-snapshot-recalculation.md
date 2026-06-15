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

## Frontend Delivery Contract

- Follow `docs/backlog/frontend-delivery-contract.md`, `docs/architecture/frontend/ui-design-spec.md`, `docs/architecture/frontend/frontend-architecture.md` and ADR-0007.
- Implement the owned App Router route with the approved `(app)` shell, existing GastroLedger design tokens and shadcn/ui-derived primitives; add shared primitives only for confirmed consumers.
- Define and test every applicable loading, empty, validation/error, unauthorized, success, stale/conflict and destructive state without enabling unimplemented behavior.
- Verify keyboard/focus/accessibility behavior and responsive rendering at 390, 1024 and 1440 CSS pixels with no horizontal scroll at 390.
- Record component or feature tests, integrated route evidence and visual QA evidence. No external UI assets, APIs or services are allowed.
## Definition Of Done

- [ ] TC-010-S/A/F and IT-003/018/019/020 pass.
- [ ] Worker jobs carry tenant context and expose correlation evidence.
- [ ] No broker or external service is introduced.
- [ ] Required root quality commands and `regression-gate` pass.
