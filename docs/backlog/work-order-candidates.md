# Work Order Candidates

```text
status = proposed only
approved_by_user = false
base_branch = develop
target_branch = develop
required_pr_check = regression-gate
```

## Completed: GL-001 Tenant Registration And Isolation Tracer

```text
work_order_id = GL-001
feature_branch = feature/GL-001-tenant-registration-isolation
readiness = done
target_agent = implementer-agent
workflow = tdd-implementation
```

Delivered objective: visible company registration that atomically creates the tenant,
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

Delivery evidence: PR #24 merged into `develop`; required root checks and PostgreSQL
integration evidence passed.

## Completed: GL-002 Local Users, Invitations And Scoped Roles

```text
work_order_id = GL-002
feature_branch = feature/GL-002-local-users-scoped-roles
readiness = done
pull_request = https://github.com/Ainsiel/GastroLedger/pull/28
```

Objective: let a tenant administrator generate a manually shared invitation and
assign a branch-scoped role while preventing privilege escalation.

This is ready because the session, tenant context and minimum Platform & Organization
persistence from `GL-001` are accepted.

Delivery evidence: PR #28 merged into `develop` on 2026-06-16 and implements
invitation generation, public invitation acceptance, local session creation,
scoped role persistence, branch visibility and dashboard access. Required root
checks and regression-gate passed before merge.

## Completed: GL-003 Tenant Operating Scope

```text
work_order_id = GL-003
feature_branch = feature/GL-003-tenant-operating-scope
readiness = done
pull_request = https://github.com/Ainsiel/GastroLedger/pull/26
```

Delivered objective: configure tenant settings and create/deactivate branches and
warehouses with enforced limits and audit evidence.

Delivery evidence: PR #26 merged into `develop`.

## Completed: GL-004 Units And Ingredient Catalog

```text
work_order_id = GL-004
feature_branch = feature/GL-004-units-ingredient-catalog
readiness = done
pull_request = https://github.com/Ainsiel/GastroLedger/pull/27
```

Delivered objective: manage units, conversion factors and ingredients under the
Menu Engineering route.

Delivery evidence: PR #27 merged into `develop`.

## Current Ready Candidates

```text
GL-005 Manage suppliers and effective-dated offers
GL-006 Approve versioned sub-recipes
GL-016 Apply manual ordering holds
GL-019 Reconcile an operational cash shift
GL-020 Plan shifts and record attendance
```

## Approval Contract

Ready candidates are not approved work orders. Approval must name one candidate,
its scope and AFK delegation separately before implementation begins.
