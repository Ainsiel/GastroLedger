# Architecture Pattern Selection Skill

## Purpose

Select system-level patterns from confirmed forces rather than fashion.

## Procedure

1. Restate the problem, drivers, constraints and expected change profile.
2. Establish the simplest viable baseline, normally a modular monolith.
3. Compare only plausible alternatives.
4. Evaluate operational cost, consistency, coupling, testability, deployment and team ownership.
5. Identify failure modes and exit criteria for each option.
6. Recommend one approach and state what evidence would invalidate it.
7. Record consequential choices as an ADR.

## Candidate Families

Consider only when relevant:

- layered or modular monolith;
- hexagonal or ports-and-adapters structure;
- microservices;
- event-driven architecture;
- CQRS;
- event sourcing;
- pipeline, plugin or workflow architecture;
- serverless or batch-oriented processing.

## Selection Rules

- Microservices require a clear independent deployment or ownership benefit.
- Event-driven integration requires ownership, delivery, ordering, retry and observability decisions.
- CQRS requires materially different read and write needs.
- Event sourcing requires audit/history value that exceeds its operational complexity.
- A pattern may apply to one bounded context without becoming the whole-system architecture.

Use `pattern-decision.md`. Do not combine several expensive patterns without separate justification.
