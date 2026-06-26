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
GL-014 Perform a blind count and reconcile variance
GL-015 Import sales and resolve allocation exceptions
GL-016 Apply manual ordering holds
GL-018 Record supplier return and expected adjustment
GL-019 Reconcile an operational cash shift
GL-020 Plan shifts and record attendance
```

## In PR: GL-013 Expiry Alerts

```text
work_order_id = GL-013
feature_branch = feature/GL-013-expiry-alerts
readiness = in_pr
pull_request = https://github.com/Ainsiel/GastroLedger/pull/37
```

Delivery evidence: PR #37 targets `develop` and implements leased expiry scanning,
deduplicated in-app alerts, tenant isolation, acknowledgement evidence and active or
acknowledged inventory views. Visual QA is intentionally skipped per user instruction.

## Completed: GL-012 Operational Waste

```text
work_order_id = GL-012
feature_branch = feature/GL-012-operational-waste
readiness = done
pull_request = https://github.com/Ainsiel/GastroLedger/pull/36
```

Delivery evidence: PR #36 merged into `develop` on 2026-06-20 and implements
approval-gated waste, append-only correction, audit evidence and visible inventory
states. Visual QA was intentionally skipped per user instruction.

## Completed: GL-011 Stock Transfer Lifecycle

```text
work_order_id = GL-011
feature_branch = feature/GL-011-stock-transfer-lifecycle
readiness = done
pull_request = https://github.com/Ainsiel/GastroLedger/pull/35
```

Delivery evidence: PR #35 merged into `develop` on 2026-06-20 and implements request,
approval, FEFO/FIFO dispatch, idempotent receipt/loss reconciliation and destination
lot lineage. Visual QA is intentionally skipped per user instruction.

## Completed: GL-010 Production Batch

```text
work_order_id = GL-010
feature_branch = feature/GL-010-production-batch
readiness = done
pull_request = https://github.com/Ainsiel/GastroLedger/pull/34
```

Delivery evidence: PR #34 merged into `develop` on 2026-06-20 and implements atomic
FEFO/FIFO input allocation, immutable production entries, prepared-lot lineage and
visible yield/shortage states. Visual QA is intentionally skipped per user instruction.

## Completed: GL-009 Supplier Receipt Inventory Ledger

```text
work_order_id = GL-009
feature_branch = feature/GL-009-supplier-receipt-inventory-ledger
readiness = done
pull_request = https://github.com/Ainsiel/GastroLedger/pull/33
```

Delivery evidence: PR #33 merged into `develop` on 2026-06-19 and implements atomic,
idempotent supplier receipts, traceable lots, immutable entries and non-negative
balance projections. Visual QA is intentionally skipped per user instruction.

## Completed: GL-008 Cost Snapshot Recalculation

```text
work_order_id = GL-008
feature_branch = feature/GL-008-cost-snapshot-recalculation
readiness = done
pull_request = https://github.com/Ainsiel/GastroLedger/pull/32
```

Delivery evidence: PR #32 merged into `develop` on 2026-06-19 and implements
PostgreSQL outbox/jobs, idempotent cost projections, retry evidence and visible
snapshot state. Required CI and regression-gate passed before merge. Visual QA
was intentionally skipped per user instruction.

## Completed: GL-007 Menu Items And Branch Margin

```text
work_order_id = GL-007
feature_branch = feature/GL-007-menu-items-margin
readiness = done
pull_request = https://github.com/Ainsiel/GastroLedger/pull/31
```

Delivery evidence: PR #31 merged into `develop` on 2026-06-19 and implements
menu-item approval, immutable cost snapshots and effective-dated branch margin
views. Required CI and regression-gate passed before merge. Visual QA was
intentionally skipped per user instruction.

## Completed: GL-006 Versioned Sub-Recipes

```text
work_order_id = GL-006
feature_branch = feature/GL-006-versioned-sub-recipes
readiness = done
pull_request = https://github.com/Ainsiel/GastroLedger/pull/30
```

Delivery evidence: PR #30 merged into `develop` on 2026-06-19 and implements
immutable sub-recipe version approval, initial theoretical cost snapshots and
scheduled version handling. Required CI and regression-gate passed before merge.

## Completed: GL-005 Suppliers And Effective Offers

```text
work_order_id = GL-005
feature_branch = feature/GL-005-suppliers-effective-offers
readiness = done
pull_request = https://github.com/Ainsiel/GastroLedger/pull/29
```

Delivery evidence: PR #29 merged into `develop` on 2026-06-16 and implements
tenant-scoped suppliers and effective-dated ingredient offers under Procurement.
Required root checks and regression-gate passed before merge.

## Approval Contract

Ready candidates are not approved work orders. Approval must name one candidate,
its scope and AFK delegation separately before implementation begins.
