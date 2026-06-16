---
id: GL-016
title: Apply manual ordering holds
status: draft
readiness: ready
primary_context: Control & Insights
labels: [gridwork, type:feature, slice:vertical, status:ready]
dependencies: [GL-002, GL-003]
requirements: [FR-025, FR-027]
use_cases: [UC-024]
flows: [UC-024-A, UC-024-F]
test_cases: [TC-024-A, TC-024-F]
quality_attributes: [QA-009, QA-010, QA-012]
---

# Goal

A franchise controller can manually apply or release a reasoned ordering hold, and
purchase approval can query the resulting public decision.

## Scope

- Frontend: hold state, reason and controlled apply/release workflow.
- API: hold command/query and public `OrderingHoldDecision` contract.
- Domain/application: authorization, reason and effective-period policy.
- Persistence: ordering hold lifecycle and audit evidence.
- Tests: apply/release, missing reason, forbidden actor and procurement decision.

## Exclusions

- Automatic debt enforcement, collections, invoices and royalty calculation.

## Acceptance Criteria

- [ ] Authorized apply/release changes the public ordering decision with reason.
- [ ] Missing reason or forbidden actor changes nothing and is audited.
- [ ] Procurement can query the decision without reading Control internals.
- [ ] Holds remain manually governed and non-financial.

## Frontend Delivery Contract

- Follow `docs/backlog/frontend-delivery-contract.md`, `docs/architecture/frontend/ui-design-spec.md`, `docs/architecture/frontend/frontend-architecture.md` and ADR-0007.
- Implement the owned App Router route with the approved `(app)` shell, existing GastroLedger design tokens and shadcn/ui-derived primitives; add shared primitives only for confirmed consumers.
- Define and test every applicable loading, empty, validation/error, unauthorized, success, stale/conflict and destructive state without enabling unimplemented behavior.
- Verify keyboard/focus/accessibility behavior and responsive rendering at 390, 1024 and 1440 CSS pixels with no horizontal scroll at 390.
- Record component or feature tests, integrated route evidence and visual QA evidence. No external UI assets, APIs or services are allowed.
## Definition Of Done

- [ ] TC-024-A/F and the public ordering-hold decision contract pass.
- [ ] Cross-context dependency uses the existing public contract.
- [ ] No payment, debt or collection behavior is introduced.
- [ ] Required root quality commands and `regression-gate` pass.
