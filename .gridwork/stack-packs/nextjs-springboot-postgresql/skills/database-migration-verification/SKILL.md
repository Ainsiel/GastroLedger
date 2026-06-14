# Database Migration Verification

## Purpose

Verify database migrations across clean install and approved upgrade paths.

## Procedure

1. Read the migration and rollback strategy.
2. Verify migration from an empty database.
3. Verify the supported upgrade path.
4. Start the application against the migrated schema.
5. Assess backward-compatible deployment windows.
6. Detect destructive or long-locking operations.
7. Record release and rollback implications.

## Evidence

- Record migration versions and schema results.
- Record startup, compatibility and timing evidence.

## Guardrails

- Use isolated disposable databases.
- Flag data-loss and lock risks for explicit review.
- Do not generate during Gridwork installation.
