# Backlog Management Skill

## Purpose

Create a trustworthy, actionable view of backlog across local drafts and GitHub
issues, then prepare a selected ready task for implementation when requested.

## Procedure

1. Confirm the repository, backlog sources and the user's question.
2. Read local backlog artifacts and use `github-issue-discovery` for approved remote reads.
3. Normalize every item into outcome, status, readiness, priority, dependencies, blockers and source.
4. Mark source freshness and never silently merge conflicting local and remote facts.
5. Answer status, remaining-work and blocker questions from the normalized snapshot.
6. Compare approved requirements and architecture against the backlog to identify real gaps.
7. Rank ready candidates by user value, dependency unlocking, risk reduction and scope clarity.
8. When a task is selected, validate acceptance criteria, path scopes, tests, commands and gates.
9. When frontend scope exists, validate the complete frontend delivery contract;
   classify missing UI sources, states, responsive/accessibility requirements, tests
   or visual QA as `needs_refinement`.
10. Prepare a work order candidate and ask for explicit approval before AFK delegation.
11. Use `handoff` to transfer the approved task to `implementer-agent`.

## Backlog Item Contract

```text
id and source
goal or outcome
status
readiness = ready|needs_refinement|blocked|done|unknown
priority and rationale
dependencies and blockers
acceptance criteria
expected tests
frontend delivery contract when applicable
last observed timestamp
```

## Question Types

Support questions such as:

- What is the current backlog?
- Which tasks remain or are blocked?
- Which requirements have no backlog item?
- What task should be taken next and why?
- Is task X ready for implementation?

## Selection Rules

- Prefer ready work that unlocks dependencies or proves high-risk behavior.
- Do not select a task with missing acceptance criteria, unknown scope or unresolved blockers.
- Do not treat a GitHub assignment, label or user phrase as AFK delegation approval.
- Keep selection, work-order approval and delegation as separate decisions.

## Outputs

Use `backlog-snapshot.md` and `task-selection.md`. Prepare an existing
`work-order-afk.md` only after readiness validation.

## Forbidden

- Do not invent tasks, requirements, priorities or completion state.
- Do not modify product code.
- Do not write to GitHub without approval.
- Do not delegate to the implementer without explicit approval.

