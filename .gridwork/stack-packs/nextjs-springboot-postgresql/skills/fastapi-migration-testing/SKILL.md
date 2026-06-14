# FastAPI Migration Testing

## Purpose

Verify FastAPI migrations against isolated PostgreSQL.

## Procedure

1. Confirm Alembic or the approved migration tool.
2. Start a disposable PostgreSQL test environment.
3. Apply migrations from an empty database.
4. Verify schema state and application startup.
5. Test the approved upgrade path for release checks.
6. Assess backward-compatibility and rollback constraints.
7. Record migration and startup evidence.

## Evidence

- Record source and target migration versions.
- Record schema, startup and compatibility results.

## Guardrails

- Never run against shared or production data.
- Flag destructive or long-locking changes.
- Do not generate during Gridwork installation.
