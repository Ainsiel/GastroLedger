---
id: GL-009
title: Receive a supplier delivery into the inventory ledger
status: done
readiness: done
primary_context: Procurement
labels: [gridwork, type:feature, slice:vertical]
dependencies: [GL-005]
pull_request: https://github.com/Ainsiel/GastroLedger/pull/33
merged_at: 2026-06-19T22:12:12Z
merge_commit: f3ded99cd936bf39b6d37addb366f3713ce664aa
requirements: [FR-013, FR-020, FR-027]
use_cases: [UC-013]
test_cases: [TC-013-S, TC-013-A, TC-013-F, IT-008, IT-009, IT-010]
quality_attributes: [QA-002, QA-003, QA-010, QA-012]
---

# Goal

A warehouse operator can receive an acceptable supplier delivery and atomically
create traceable lots, receipt evidence and one immutable inventory transaction.

## Scope

- Frontend: receiving form with accepted, partial and rejected-line states.
- API: receipt command/result and Procurement-to-Inventory event contract.
- Domain/application: temperature/tolerance, duplicate lot, partial receipt and
  idempotency policy.
- Persistence: receipt/line relations plus minimum lot, immutable ledger and balance
  projection relations.
- Tests: receipt atomicity, retry idempotency and concurrent no-negative constraint.

## Exclusions

- Purchase-order creation behavior, supplier payment, invoices and accounting.
- Tests may seed an open order reference until GL-017 delivers order creation.

## Acceptance Criteria

- [ ] An accepted receipt commits receipt lines, lots, costs and one balanced
  inventory transaction atomically.
- [ ] A partial receipt posts accepted quantity and preserves the open remainder.
- [ ] Rejected temperature, duplicate lot or excess blocks affected lines.
- [ ] Retrying the same acceptance creates no duplicate lot or ledger entry.
- [ ] No committed balance becomes negative.

## Frontend Delivery Contract

- Follow `docs/backlog/frontend-delivery-contract.md`, `docs/architecture/frontend/ui-design-spec.md`, `docs/architecture/frontend/frontend-architecture.md` and ADR-0007.
- Implement the owned App Router route with the approved `(app)` shell, existing GastroLedger design tokens and shadcn/ui-derived primitives; add shared primitives only for confirmed consumers.
- Define and test every applicable loading, empty, validation/error, unauthorized, success, stale/conflict and destructive state without enabling unimplemented behavior.
- Verify keyboard/focus/accessibility behavior and responsive rendering at 390, 1024 and 1440 CSS pixels with no horizontal scroll at 390.
- Record component or feature tests, integrated route evidence and visual QA evidence. No external UI assets, APIs or services are allowed.
## Definition Of Done

- [ ] TC-013-S/A/F and IT-008/009/010 pass.
- [ ] Cross-context writes occur through the approved event/application contract.
- [ ] Actor, time, reason and correlation evidence are retained.
- [ ] Required root quality commands and `regression-gate` pass.
