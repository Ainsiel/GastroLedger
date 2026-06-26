# Clean Architecture Skill

## Purpose

Design dependency direction so business rules and use cases remain testable and independent from UI, frameworks, databases and external services.

## Procedure

1. Start from bounded contexts and use cases, not folder names.
2. Identify domain policy, application orchestration and external mechanisms.
3. Make dependencies point toward stable business policy.
4. Define input ports only where callers need a stable use-case contract.
5. Define output ports only at real volatile or external boundaries.
6. Assign adapters to delivery, persistence and integration mechanisms.
7. Map transaction, authorization and observability responsibilities explicitly.
8. Validate important use cases can be tested without starting every external mechanism.

## Decision Rules

- Prefer a direct call over an interface when there is no meaningful boundary.
- Introduce a port when volatility, replaceability, isolation or ownership makes it valuable.
- Keep framework annotations and transport DTOs outside the domain model.
- Keep application services focused on orchestration and transaction intent.
- Do not force identical layers in every bounded context.

## Output

Produce:

```text
dependency-rules.md
port-adapter-map.md
use-case-boundaries.md
```

Each proposed port must state:

```text
consumer
responsibility
reason_for_boundary
known_adapters
failure_contract
test_strategy
```

## Avoid

- Interfaces for every class.
- Pass-through layers that add no policy.
- Domain objects coupled to persistence or HTTP contracts.
- A shared domain model across bounded contexts.
