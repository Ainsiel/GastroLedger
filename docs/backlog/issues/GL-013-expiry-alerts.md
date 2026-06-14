---
id: GL-013
title: Create and acknowledge expiry alerts
status: draft
readiness: blocked
primary_context: Inventory & Production
labels: [gridwork, type:feature, slice:vertical]
dependencies: [GL-008, GL-009]
requirements: [FR-018, FR-029]
use_cases: [UC-019]
test_cases: [TC-019-S, TC-019-A, TC-019-F]
quality_attributes: [QA-002, QA-007, QA-013]
---

# Goal

The worker creates deduplicated in-app alerts for lots nearing expiry, and an
operator can acknowledge an alert with an action note.

## Scope

- Frontend: active and acknowledged expiry-alert views.
- API/worker: alert query, acknowledgement and scheduled job contracts.
- Domain/application: FEFO expiry threshold, deduplication and acknowledgement.
- Persistence: expiry alert and in-app notification state.
- Tests: due-lot alert creation, acknowledgement and repeated-job idempotency.

## Exclusions

- Email, SMS, push APIs and autonomous disposal.

## Acceptance Criteria

- [ ] Due lots produce active tenant/warehouse-scoped in-app alerts.
- [ ] Acknowledgement retains actor, time and action note.
- [ ] Repeated worker execution creates no duplicate active alert.
- [ ] Other tenants cannot observe the alert or lot.

## Definition Of Done

- [ ] TC-019-S/A/F pass with real worker/PostgreSQL boundaries.
- [ ] Alert delivery uses no external service.
- [ ] Job retry and tenant context evidence are retained.
- [ ] Required root quality commands and `regression-gate` pass.
