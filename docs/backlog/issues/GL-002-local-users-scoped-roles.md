---
id: GL-002
title: Manage local users, invitations and scoped roles
status: draft
readiness: blocked
primary_context: Platform & Organization
labels: [gridwork, type:feature, slice:vertical, mode:afk, agent:implementer, workflow:tdd-implementation]
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

- [ ] A valid scoped role grants only its named tenant or branch capabilities.
- [ ] A generated invitation is hashed, expiring, manually shareable and usable
  once.
- [ ] Expired invitations and privilege escalation are denied and audited.
- [ ] Other branches and tenants remain hidden from a branch-scoped user.

## Definition Of Done

- [ ] TC-003-S/A/F and IT-004 pass.
- [ ] Protected actions include actor, reason/correlation and audit evidence.
- [ ] Frontend authorized/unauthorized states are covered.
- [ ] Required root quality commands and `regression-gate` pass.
