# Architecture Grill Me Skill

## Purpose

Run an adaptive interview that discovers the architectural drivers hidden behind an approved SDD. Produce decisions and open questions, not a generic checklist dump.

## Procedure

1. Read the SDD, use cases, test cases and known constraints.
2. Extract confirmed facts, assumptions, contradictions and missing quality scenarios.
3. Ask one focused question at a time, explaining why the answer affects architecture.
4. Start with domain and business risk, then cover quality attributes, integrations, data, security and operations.
5. Follow important answers with consequence questions.
6. Record each answer in `architecture-questionnaire.md`.
7. Recommend only the architecture skills needed for unresolved or high-impact decisions.
8. Stop interviewing when the remaining unknowns are low impact or explicitly deferred.

## Question Branches

Use branches when relevant:

- domain: core capability, experts, rules, lifecycle, terminology, ownership;
- scale: load shape, latency, throughput, growth, hot paths;
- reliability: failure tolerance, recovery targets, consistency, offline behavior;
- integration: consumers, providers, protocols, contracts, ownership;
- data: privacy, retention, audit, residency, migration, reporting;
- security: actors, trust boundaries, authorization, threats;
- delivery: team ownership, deployability, environments, observability, cost.

Convert vague qualities into scenarios:

```text
stimulus + operating condition + expected response + measurable threshold
```

## Skill Selection

- Use `ubiquitous-language` when terms conflict or carry business meaning.
- Use `domain-driven-design` when domain complexity and ownership matter.
- Use `clean-architecture` when dependency direction or testability needs design.
- Use pattern skills only for a concrete force or problem.
- Use diagram skills only when a visual answers an identified question.

## Completion

Produce:

```text
architecture-questionnaire.md
architecture-drivers.md
skill-selection-plan.md
open-decisions.md
```

Do not decide uncertain architecture silently. Mark it as a human gate.
