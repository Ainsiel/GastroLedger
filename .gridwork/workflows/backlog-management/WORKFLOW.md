# Backlog Management Workflow

## Purpose

Maintain an actionable view of local and GitHub backlog, answer management questions,
identify missing work and prepare selected ready tasks for implementation.

## When To Use

Use when the user asks what the backlog contains, what remains, what is blocked, what
should be done next, or asks the backlog manager to take a task.

## When Not To Use

Do not use for direct implementation, architecture design, PR verification or
unapproved GitHub writes.

## Participating Agents

```text
primary_agent = backlog-manager-agent
supporting_agents = orchestrator,planner-agent,implementer-agent
mode = interactive
```

## Allowed Skills

```text
backlog-management
backlog-planning
github-issue-discovery
github-issue-publisher
github-label-manager
github-cli
handoff
```

## Phases

1. Confirm whether the requested view includes local drafts, GitHub issues or both.
2. Read local backlog artifacts and optionally use governed GitHub issue discovery.
3. Normalize items, dependencies, status, readiness, blockers and missing context.
4. Answer the user's backlog question using a timestamped snapshot.
5. Identify missing tasks only from approved requirements, architecture or observed gaps.
6. If the user asks to take a task, recommend or validate one ready candidate.
7. When frontend scope exists, validate the issue and work order against
   `frontend-delivery-policy.md`; incomplete frontend contracts are
   `needs_refinement`, not `ready`.
8. Prepare a complete implementation work order candidate and selection record.
9. Ask for explicit approval of the work order and AFK delegation.
10. After approval, hand off to `implementer-agent` using `tdd-implementation`.
11. Prepare GitHub updates only when requested and execute them only after a separate approval.

## Human Gates

Stop before GitHub writes, changing priority or scope, approving a work order,
delegating AFK work, or modifying product code.

## Artifacts

```text
.factory/runs/<run-id>/artifacts/backlog-management/backlog-snapshot.md
.factory/runs/<run-id>/artifacts/backlog-management/gap-analysis.md
.factory/runs/<run-id>/artifacts/backlog-management/task-selection.md
.factory/runs/<run-id>/artifacts/backlog-management/work-order-candidate.md
.factory/runs/<run-id>/handoffs/backlog-manager-to-implementer.md
```

Approved local backlog documents may be written to `docs/backlog/`.

## Completion Criteria

The workflow can close after the question is answered, backlog gaps are documented,
or an approved task has been handed to the implementer.

