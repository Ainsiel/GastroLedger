# API Contract Design Skill

## Purpose

Design APIs as explicit consumer contracts aligned to use cases and bounded-context ownership.

## Procedure

1. Identify consumers, jobs-to-be-done and trust boundaries.
2. Decide synchronous, asynchronous or batch interaction from latency and coupling needs.
3. Design operations around business capabilities, not database tables.
4. Define request, success, error, authorization and idempotency behavior.
5. Define pagination, filtering, sorting, limits and concurrency semantics where relevant.
6. Separate public contract models from internal domain and persistence models.
7. Define compatibility and deprecation strategy.
8. Define contract tests and observability signals.

## Contract Rules

- Use stable domain language.
- Make validation errors actionable and machine-readable.
- Do not leak stack traces, persistence details or internal identifiers unnecessarily.
- Make retry behavior safe and explicit.
- For events, define producer, owner, schema, delivery semantics, ordering and evolution.
- For long-running work, define accepted status and progress/result retrieval.

## Output

Use `api-design.md` and include example payload shapes without real secrets or sensitive data.

## Avoid

- CRUD endpoints as the automatic default.
- One endpoint per UI component.
- Unbounded collections.
- Breaking changes without a migration path.
- Shared DTOs across bounded contexts.
