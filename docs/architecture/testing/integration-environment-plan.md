# Integration Environment Plan

## Lifecycle

1. Start an isolated PostgreSQL database or schema per test worker.
2. Apply the exact production migration chain and RLS policies.
3. Seed only the tenant, users and domain records needed by the scenario.
4. Run FastAPI API/worker boundaries with deterministic clock and identifiers.
5. Capture actionable evidence on failure.
6. Drop the isolated database/schema after the suite.

## Isolation

- No shared mutable QA database.
- No Internet or external APIs.
- Tests create their own tenants and never depend on execution order.
- Concurrency tests use explicit barriers instead of timing guesses.
- Migration verification begins from an empty database and supported prior schema.

## Future Commands

Exact commands are deferred until `repository-bootstrap` confirms Python, Node,
migration and test tooling. Architecture defines the required suites, not invented
commands.
