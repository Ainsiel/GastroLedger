# Handoff Skill

## Purpose

Create a concise transfer summary when another agent or another session must continue the work.

## When To Use

Use this skill when:

- responsibility moves from one agent to another;
- the user wants to continue in a new session;
- verification needs context from implementation;
- a run is blocked and someone else must pick it up.

## When Not To Use

Do not use this skill:

- after every small step;
- as a substitute for logs or reports;
- to copy complete command output;
- to store secrets or sensitive data.

## Allowed Agents

```text
orchestrator
intake-agent
software-architect
architecture-foundation-agent
planner-agent
backlog-manager-agent
implementer-agent
verifier-agent
release-manager-agent
```

## Compatible Workflows

```text
intake-existing-code
ideation-from-zero
architecture-ddd
architecture-foundation
backlog-management
tdd-implementation
verification-pr
feature-pr-delivery
release-promotion
```

## Required Inputs

- `run_id`
- source agent or session
- target agent or session
- current status
- decisions made
- artifacts created
- pending gates
- next steps

## Outputs

Write or propose a Markdown summary for:

```text
.factory/runs/<run-id>/handoff.md
```

If there are multiple transfers, use:

```text
.factory/runs/<run-id>/handoffs/<sequence>-<source>-to-<target>.md
```

## Procedure

1. Summarize the user request.
2. List decisions already made.
3. List artifacts and files created or changed.
4. List commands or checks as summaries only.
5. List risks, blockers and pending approvals.
6. State the next recommended action.
7. Redact sensitive data and omit secrets.

## Permissions

This skill never raises permissions. It can only write artifacts allowed by the active agent, workflow and path scopes.

## Human Gates

Stop if the summary would require secret values, private credentials or sensitive data that cannot be safely redacted.

## Traceability

When a run exists, record that the handoff was created in the run timeline.
