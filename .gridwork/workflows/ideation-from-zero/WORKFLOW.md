# Ideation From Zero Workflow

## Purpose

Transform a rough product idea into normalized requirements and an SDD-oriented document set.

## When To Use

Use this workflow when the user wants to design a new product or system from an idea and there is not yet an approved SDD.

## When Not To Use

Do not use this workflow for direct implementation, PR review, release publishing or architecture decisions after an SDD already exists.

## Preconditions

- The user has provided an idea or product direction.
- The orchestrator has loaded factory policies.
- The user expects HITL clarification.

## Participating Agents

```text
primary_agent = intake-agent
supporting_agents = orchestrator
```

## Allowed Skills

```text
sdd-requirements
handoff
```

## Phases

1. Capture the idea, goals, users and constraints.
2. Ask grill-me questions until ambiguity is reduced.
3. Split answers into separate Markdown notes when useful.
4. Normalize capabilities, use cases, non-functional needs and risks.
5. Use `sdd-requirements` to generate an SDD draft.
6. Ask the user to approve, revise or continue discovery.

## Human Gates

Stop before treating assumptions as requirements, versioning an approved SDD, delegating implementation or publishing issues.

## Artifacts

Draft artifacts live in:

```text
.factory/runs/<run-id>/artifacts/ideation/
```

Approved SDD artifacts may be written to:

```text
docs/sdd/
```

## Completion Criteria

The workflow can close when the user accepts the SDD draft or chooses to continue ideation.

