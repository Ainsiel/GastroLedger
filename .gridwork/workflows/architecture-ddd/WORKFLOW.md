# Architecture DDD Workflow

## Purpose

Design the system from an approved SDD using an adaptive architecture grill-me, DDD strategic design and optional technical skills. Produce approved architecture outputs ready for backlog planning.

## When To Use

Use this workflow after the SDD is ready and the user wants architecture, APIs, database guidance, ADRs and vertical slice planning.

## When Not To Use

Do not use this workflow to implement code, publish issues without approval or run CI/CD.

## Participating Agents

```text
primary_agent = software-architect
supporting_agents = orchestrator,planner-agent
```

## Allowed Skills

```text
architecture-grill-me
ubiquitous-language
domain-driven-design
clean-architecture
architecture-pattern-selection
design-pattern-selection
api-contract-design
relational-data-modeling
architecture-decision-records
integration-test-design
integration-testing
html-architecture-diagrams
c4-html-diagrams
erd-html-diagrams
uml-html-diagrams
backlog-planning
github-label-manager
github-actions-cicd
monorepo-layout-design
docker-compose-environment-strategy
rollback-planning
conditional stack-pack skills
handoff
```

## Phases

1. Read the approved SDD and use `architecture-grill-me` to identify drivers, constraints and uncertain decisions.
2. Establish ubiquitous language and perform DDD strategic design.
3. Select only the optional skills justified by the grill-me results.
4. Design technical boundaries, APIs, data, security, operations and quality-attribute responses.
5. Record consequential decisions as ADRs.
6. Produce C4, ERD, UML or other HTML diagrams only when they answer a defined question.
7. Review the complete design for traceability, simplicity, risks and contradictions.
8. When a frontend exists, explicitly design feature boundaries, route ownership,
   server/client boundaries, state ownership, API consumption, auth/security and tests.
9. Ask for approval before promoting architecture drafts to `docs/architecture/` or `docs/adr/`.
10. Define repository boundaries, Compose environments and rollback constraints when the project needs them.
11. Prepare repository and materialization constraints; route greenfield scaffolding through `repository-bootstrap` before `architecture-foundation`.
12. Use `backlog-planning` for functional vertical-slice drafts after foundation, or earlier only when their foundation dependency is explicit.
13. Use `github-label-manager` only to audit predefined labels or prepare an approved missing-label plan.

## Optional Skill Rule

The workflow does not require every architecture or diagram skill. The architect must create `skill-selection-plan.md` explaining:

```text
selected skill
decision or question it answers
required input
expected output
reason omitted when a commonly expected artifact is unnecessary
```

## Human Gates

Stop before writing CI files, publishing GitHub issues, deciding uncertain architecture or changing product code.

## Artifacts

Draft outputs live in `.factory/runs/<run-id>/artifacts/architecture/`.

Approved architecture may be written to:

```text
docs/architecture/
docs/adr/
```

HTML diagrams must be self-contained local files without CDN or build step.

Recommended architecture artifact set:

```text
architecture-questionnaire.md
architecture-drivers.md
architecture-overview.md
domain/ubiquitous-language.md
domain/context-map.md
adrs/
optional api/, data/, diagrams/ and structure/ outputs
```

## Completion Criteria

The workflow can close when architecture outputs are approved and ready for `repository-bootstrap` or `architecture-foundation`.
