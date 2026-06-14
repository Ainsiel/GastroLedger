# Intake Existing Code Workflow

## Purpose

Transform an ambiguous request about an existing project into clarified, actionable next steps.

## When To Use

Use this workflow for:

- bug reports;
- feature requests;
- improvement ideas;
- requests to inspect existing code before planning.

## When Not To Use

Do not use this workflow to:

- implement code immediately;
- create GitHub issues without approval;
- perform AFK delegation;
- design a full system from zero.

## Preconditions

- The user provided a request.
- The orchestrator loaded factory, policy, workflow and skill contracts.
- No secret values are required.

## Participating Agents

```text
primary_agent = intake-agent
supporting_agents = orchestrator,planner-agent
```

## Allowed Skills

```text
diagnose-bug
github-issue-discovery
github-label-manager
handoff
```

## Phases

1. Restate the request in neutral language.
2. Classify it as bug, improvement, feature, refactor, investigation or unknown.
3. Identify missing context and ask concise questions if needed.
4. Identify likely affected areas without modifying code.
5. Optionally prepare an issue draft or work order candidate in `.factory/`.
6. Create `.factory/` runtime artifacts only after the user chooses to continue.
7. Propose next step: continue intake, publish issue draft, route to TDD, or ask for approval.
8. If issue publication is selected, audit catalog labels before any publish plan.

## Human Gates

Stop before:

- writing code;
- creating, editing or commenting GitHub issues;
- delegating AFK work;
- running non-read-only commands;
- reading secret values;
- changing architecture or dependencies.

## Artifacts

When a run is created, artifacts live under:

```text
.factory/runs/<run-id>/
```

Minimal expected artifacts:

- `summary.md`
- `run.json`
- `events.jsonl`

## Completion Criteria

The workflow can stop when the user has a clear next step, a clarified request or an explicit decision to route into another workflow.

## Traceability

Record important decisions in runtime artifacts when a run exists. Do not write operational logs into versioned docs automatically.

## Handoff

Use handoff only when another agent or another session must continue.
