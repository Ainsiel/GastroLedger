# Backlog Planning Skill

## Purpose

Turn approved requirements and architecture into ordered, independently verifiable vertical-slice issue drafts.

## Procedure

1. Read the approved SDD, architecture overview, ADRs and bounded-context ownership.
2. Build a lightweight capability and dependency map.
3. Identify the smallest end-to-end tracer slice that proves the architecture.
4. Slice remaining behavior by user outcome or business capability, not technical layer.
5. Keep each issue inside one primary bounded context when feasible.
6. Include acceptance criteria, expected tests, path hints, dependencies, risks and exclusions.
7. For frontend scope, include the complete contract from
   `frontend-delivery-policy.md` and approved UI source references.
8. Validate labels against `github-labels.json`.
9. Review readiness before creating a publish plan.
10. Write local drafts first; publish only through `github-issue-publisher`.

## Vertical Slice Test

An issue is a good slice when it:

- delivers observable behavior;
- can be accepted and tested independently;
- includes required UI, API, domain and persistence changes together when applicable;
- does not require unrelated future issues to prove it works;
- is small enough for one controlled TDD work order.

Use enabling slices only for genuine shared infrastructure. State the user-facing slice they unlock.

## Issue Contract

Each draft must include:

```text
goal and user/domain outcome
context and source requirements
scope and exclusions
acceptance criteria
expected tests
dependencies
risks and rollout notes
catalog labels
definition of done
visible frontend behavior when applicable
affected frontend feature and route
server/client boundary
frontend state ownership
API consumption contract
expected frontend and accessibility tests
approved UI sources and component system
responsive viewports and visual QA evidence
```

## Ordering

Prioritize:

1. architecture/risk tracer;
2. core domain behavior;
3. high-value vertical slices;
4. supporting behavior;
5. optimization backed by evidence.

## Gates

- Use `github-label-manager` before publication when labels are missing.
- Require review before publish.
- Require user approval before AFK delegation.

## Outputs

```text
.factory/runs/<run-id>/artifacts/backlog/issues/
.factory/runs/<run-id>/artifacts/backlog/publish-plan.md
.factory/runs/<run-id>/artifacts/backlog/work-order-candidates/
```

## Forbidden

- Do not publish GitHub issues directly.
- Do not invent labels.
- Do not mark a draft publishable while it references an unknown label.
- Do not split work horizontally by layer when it harms verification.
- Do not create vague umbrella issues that cannot be accepted independently.
