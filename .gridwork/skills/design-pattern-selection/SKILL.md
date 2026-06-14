# Design Pattern Selection Skill

## Purpose

Choose a local design pattern only after naming the concrete problem and proving a simpler design is insufficient.

## Procedure

1. Describe the change, variation, lifecycle or collaboration causing friction.
2. Identify what should remain stable and what must vary.
3. Describe the simplest direct implementation.
4. Compare at most three patterns that solve the actual force.
5. Show expected use with a small interface and usage example.
6. State costs, misuse risks and removal criteria.
7. Record the decision only if it affects multiple modules or future work.

## Pattern Guidance

- Strategy: interchangeable policy selected by context.
- Factory: construction varies or hides complex creation.
- Adapter: integrate an external or incompatible contract.
- Decorator: add composable behavior without branching explosion.
- State: behavior changes materially with lifecycle state.
- Specification: reusable business predicates with clear composition value.
- Saga/process manager: coordinate a long-running cross-boundary process.
- Outbox: reliably publish integration events with committed data.

## Rules

- Prefer names from the ubiquitous language over pattern names.
- Keep interfaces small and usage obvious.
- Do not use patterns to hide unclear requirements.
- Do not add an abstraction for a single hypothetical future variation.

Use `pattern-decision.md` for the result.
