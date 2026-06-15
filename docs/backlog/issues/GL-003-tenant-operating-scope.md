---
id: GL-003
title: Configure tenant settings, branches and warehouses
status: draft
readiness: ready
primary_context: Platform & Organization
labels: [gridwork, type:feature, slice:vertical, status:ready]
dependencies: [GL-001]
requirements: [FR-002, FR-004, FR-027]
use_cases: [UC-002, UC-004]
test_cases: [TC-002-S, TC-002-A, TC-002-F, TC-004-S, TC-004-A, TC-004-F]
quality_attributes: [QA-009, QA-010, QA-011]
---

# Goal

A tenant administrator can configure descriptive tenant settings and establish the
branches and internal warehouses that scope operational work.

## Scope

- Frontend: settings, branch and warehouse management under `(app)/settings`.
- API: settings update and branch/warehouse lifecycle contracts.
- Domain/application: supported setting values, operational limits, unique scoped
  codes and safe warehouse deactivation.
- Persistence: tenant settings, branches, warehouses and audit evidence.
- Tests: limit, duplicate, authorization and historical visibility scenarios.

## Exclusions

- Currency conversion, billing plans, payments and deleting historical operations.

## Acceptance Criteria

- [ ] Valid locale, descriptive base currency and operational limits are saved and
  audited.
- [ ] Reducing a limit preserves existing branches but blocks new excess creation.
- [ ] Branches and warehouses have unique tenant/branch-scoped codes.
- [ ] A warehouse with no open movements can be deactivated while history remains.
- [ ] Unsupported settings, duplicate codes and unauthorized actors change nothing.

## Frontend Delivery Contract

- Follow `docs/backlog/frontend-delivery-contract.md`, `docs/architecture/frontend/ui-design-spec.md`, `docs/architecture/frontend/frontend-architecture.md` and ADR-0007.
- Implement the owned App Router route with the approved `(app)` shell, existing GastroLedger design tokens and shadcn/ui-derived primitives; add shared primitives only for confirmed consumers.
- Define and test every applicable loading, empty, validation/error, unauthorized, success, stale/conflict and destructive state without enabling unimplemented behavior.
- Verify keyboard/focus/accessibility behavior and responsive rendering at 390, 1024 and 1440 CSS pixels with no horizontal scroll at 390.
- Record component or feature tests, integrated route evidence and visual QA evidence. No external UI assets, APIs or services are allowed.
## Definition Of Done

- [ ] TC-002-S/A/F and TC-004-S/A/F pass.
- [ ] UI exposes validation, forbidden and deactivated states.
- [ ] Tenant isolation and architecture tests remain green.
- [ ] Required root quality commands and `regression-gate` pass.
