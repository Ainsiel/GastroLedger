# PostgreSQL Persistence Guidance

## Purpose

Guide safe PostgreSQL schema, migration, transaction and persistence decisions.

## Start By Detecting

- PostgreSQL version and hosting constraints;
- migration tool and naming/order conventions;
- ORM or SQL access strategy;
- schema ownership and bounded contexts;
- confirmed persistence paths and test commands.

## Schema Rules

- Encode durable invariants with appropriate constraints.
- Make nullability, defaults and delete behavior intentional.
- Use foreign keys inside one ownership boundary when they preserve correctness.
- Use unique constraints for business uniqueness, even when surrogate identifiers exist.
- Select data types for domain semantics; avoid arbitrary text for structured values.
- Keep cross-context integration out of shared mutable tables.

## Migration Rules

- Prefer backward-compatible expand/migrate/contract changes.
- Separate schema change, data backfill and destructive cleanup for risky migrations.
- Consider lock duration, table size, rollback and application compatibility.
- Make migrations deterministic and reviewable.
- Never run destructive migrations without an explicit gate and recovery plan.

## Transactions And Repositories

- Align transactions with confirmed consistency boundaries.
- Keep transactions short.
- Define concurrency and locking behavior for contested invariants.
- Make repository contracts express domain needs rather than generic table operations.

## Verification

- Test constraints, migrations, repository behavior and transaction conflicts.
- Use realistic PostgreSQL behavior for PostgreSQL-specific features.
- Record query assumptions for later performance validation.

## Rules

- Gridwork `init` does not generate SQL or migrations.
- Implementation may edit confirmed scoped files under an approved work order.
- Do not assume migration tooling, execute destructive SQL or elevate permissions.
