---
id: GL-002
title: Manage local users, invitations and scoped roles
status: done
readiness: done
primary_context: Platform & Organization
labels: [gridwork, type:feature, slice:vertical]
dependencies: [GL-001]
requirements: [FR-003, FR-027, FR-028]
use_cases: [UC-003]
test_cases: [TC-003-S, TC-003-A, TC-003-F, IT-004]
quality_attributes: [QA-001, QA-009, QA-010, QA-011]
---

# Goal

A tenant administrator can generate a time-limited invitation for manual sharing
and assign local users tenant-wide or branch-scoped capabilities.

## Scope

- Frontend: user, invitation and role administration with permission visibility.
- API: invitation generation/acceptance and role-assignment contracts.
- Domain/application: expiry, single use, scope and anti-escalation policies.
- Persistence: users, invitations, roles, grants and membership-role assignments.
- Tests: policy TDD, API integration, audit atomicity and cross-branch isolation.

## Exclusions

- Email delivery, external identity, SMS and organization-wide SSO.

## Acceptance Criteria

- [x] A valid scoped role grants only its named tenant or branch capabilities.
- [x] A generated invitation is hashed, expiring, manually shareable and usable
  once.
- [x] Expired invitations and privilege escalation are denied and audited.
- [x] Other branches and tenants remain hidden from a branch-scoped user.

## Frontend Delivery Contract

- Follow `docs/backlog/frontend-delivery-contract.md`, `docs/architecture/frontend/ui-design-spec.md`, `docs/architecture/frontend/frontend-architecture.md` and ADR-0007.
- Implement the owned App Router route with the approved `(app)` shell, existing GastroLedger design tokens and shadcn/ui-derived primitives; add shared primitives only for confirmed consumers.
- Define and test every applicable loading, empty, validation/error, unauthorized, success, stale/conflict and destructive state without enabling unimplemented behavior.
- Verify keyboard/focus/accessibility behavior and responsive rendering at 390, 1024 and 1440 CSS pixels with no horizontal scroll at 390.
- Record component or feature tests, integrated route evidence and visual QA evidence. No external UI assets, APIs or services are allowed.
## Definition Of Done

- [x] TC-003-S/A/F and IT-004 pass.
- [x] Protected actions include actor, reason/correlation and audit evidence.
- [x] Frontend authorized/unauthorized states are covered.
- [x] Required root quality commands and `regression-gate` pass.

## Delivery Evidence

- Completed by PR #28: https://github.com/Ainsiel/GastroLedger/pull/28
- Merged into `develop` on 2026-06-16 with merge commit `259b3d67feed6d80a52581f80571336d8af87f7c`.
- CI was green before merge: branch-policy, backend, frontend, integration and regression-gate.
