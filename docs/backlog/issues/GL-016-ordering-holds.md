---
id: GL-016
title: Apply manual ordering holds
status: draft
readiness: blocked
primary_context: Control & Insights
labels: [gridwork, type:feature, slice:vertical, mode:afk, agent:implementer, workflow:tdd-implementation]
dependencies: [GL-002, GL-003]
requirements: [FR-025, FR-027]
use_cases: [UC-024-A, UC-024-F]
test_cases: [TC-024-A, TC-024-F, IT-021]
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

## Definition Of Done

- [ ] TC-024-A/F and IT-021 pass.
- [ ] Cross-context dependency uses the existing public contract.
- [ ] No payment, debt or collection behavior is introduced.
- [ ] Required root quality commands and `regression-gate` pass.
