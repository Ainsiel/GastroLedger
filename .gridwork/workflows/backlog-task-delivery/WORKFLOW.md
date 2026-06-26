# Backlog Task Delivery Workflow

## Purpose

Handle a compound request such as "find a pending backlog task, implement it and
verify it" by coordinating backlog selection, approved TDD implementation and
independent verification.

## When To Use

Use when the user wants Gridwork to select a ready pending task and carry it through
implementation and verification in one governed delivery flow.

## When Not To Use

Do not use when the user only wants backlog status, already has an approved work
order, only wants verification, or asks to bypass approvals.

## Participating Agents

```text
primary_agent = orchestrator
selection_agent = backlog-manager-agent
implementation_agent = implementer-agent
verification_agent = verifier-agent
mode = hybrid
```

## Composed Workflows

```text
backlog-management -> tdd-implementation -> feature-pr-delivery -> verification-pr
```

Each composed workflow keeps its own skills, permissions, artifacts and human gates.
The parent workflow does not grant stack or remote-write permissions.

## Phases

1. Confirm backlog sources and task-selection criteria.
2. Delegate read-only discovery and selection to `backlog-manager-agent` through
   `backlog-management`.
3. Select one ready task and prepare a complete work-order candidate.
4. For frontend scope, require the complete contract from
   `frontend-delivery-policy.md` before the task can be selected.
5. Stop for explicit approval of the exact work order and AFK delegation.
6. Delegate the approved work order to `implementer-agent` through
   `tdd-implementation`.
7. Stop at any implementation gate, including scope, dependency, unknown command,
   destructive or Git action changes.
8. Deliver the feature branch through `feature-pr-delivery`.
9. Require successful regression CI for the current PR head SHA before verifier review.
10. Hand implementation summary and TDD evidence to `verifier-agent` through `verification-pr`.
11. Produce `pass`, `changes_requested`, `needs_more_evidence` or a blocking CI state.
12. When changes are requested, return documented feedback to the implementer without
   silently expanding scope.
13. After CI and verifier pass, request merge approval and squash merge into `develop`.
14. Produce a final delivery summary. Keep each Git/GitHub write and deployment behind separate approvals.

## Approval Boundary

The initial compound request authorizes routing and read-only task discovery. It does
not approve the resulting work order, AFK delegation, code scope changes or remote
writes. The workflow must show the selected task and exact work order before asking
for the two implementation approvals.

## Human Gates

Stop before work-order approval, AFK delegation, dependency or scope changes, unknown
commands, destructive actions, Git writes, GitHub writes, PR creation, merge,
deployment or secret access.

## Artifacts

```text
.factory/runs/<run-id>/artifacts/backlog-management/backlog-snapshot.md
.factory/runs/<run-id>/artifacts/backlog-management/task-selection.md
.factory/runs/<run-id>/artifacts/backlog-management/work-order-candidate.md
.factory/runs/<run-id>/artifacts/tdd/tdd-evidence.md
.factory/runs/<run-id>/artifacts/implementation-summary.md
.factory/runs/<run-id>/artifacts/verification/verifier-report.md
.factory/runs/<run-id>/run-summary.md
```

## Completion Criteria

The workflow closes when one selected task is merged into `develop`, or when a gate,
CI result or verifier decision clearly documents why delivery cannot continue.
