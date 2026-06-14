# Work Order Candidates

```text
status = proposed only
approved_by_user = false
base_branch = develop
target_branch = develop
required_pr_check = regression-gate
```

## Candidate 1: GL-001 Tenant Registration And Isolation Tracer

```text
work_order_id = GL-001
feature_branch = feature/GL-001-tenant-registration-isolation
readiness = ready
target_agent = implementer-agent
workflow = tdd-implementation
```

Objective: deliver visible company registration that atomically creates the tenant,
first administrator and scoped local session, then prove cross-tenant isolation.

Primary paths:

- `apps/web/app/(public)/register/`, `apps/web/features/onboarding/`
- `packages/api-contract/`
- `apps/api/gastroledger_api/modules/platform_organization/`
- `apps/api/gastroledger_api/application/`, `apps/api/gastroledger_api/composition.py`
- `infra/migrations/`
- `tests/integration/`, `tests/e2e/`, `tests/architecture/`

Required local checks:

```text
npm run lint
npm test
npm run test:migrations
npm run build
```

Pending gates: work-order approval, AFK delegation, dependency changes, branch
creation, commit, push, PR creation, verifier approval and merge.

## Candidate 2: GL-002 Local Users, Invitations And Scoped Roles

```text
work_order_id = GL-002
feature_branch = feature/GL-002-local-users-scoped-roles
readiness = blocked_by_GL-001
```

Objective: let a tenant administrator generate a manually shared invitation and
assign a branch-scoped role while preventing privilege escalation.

This becomes ready only after the session, tenant context and minimum Platform &
Organization persistence from `GL-001` are accepted.

## Candidate 3: GL-003 Tenant Operating Scope

```text
work_order_id = GL-003
feature_branch = feature/GL-003-tenant-operating-scope
readiness = blocked_by_GL-001
```

Objective: configure tenant settings and create/deactivate branches and warehouses
with enforced limits and audit evidence.

This becomes ready after `GL-001`; it unlocks every branch-owned operational slice.

## Approval Contract

These are candidates, not approved work orders. Approval must name one candidate,
its scope and AFK delegation separately before implementation begins.
