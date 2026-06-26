# Relational Data Modeling Skill

## Purpose

Design relational data models that enforce confirmed invariants, preserve ownership and support known queries.

## Procedure

1. Start with domain concepts, lifecycle, ownership and retention.
2. Build a conceptual model without implementation detail.
3. Build a logical model with identities, relationships and cardinality.
4. Define constraints that the database can safely enforce.
5. Map transaction and consistency boundaries.
6. Design indexes from real query and write scenarios.
7. Identify sensitive data, audit needs and deletion behavior.
8. Define migration, compatibility and rollback strategy.

## Rules

- Prefer stable surrogate keys where appropriate; preserve business keys with unique constraints.
- Use foreign keys when they enforce ownership inside the same data boundary.
- Make nullability and defaults intentional.
- Avoid storing derived values unless performance needs and synchronization rules are explicit.
- Avoid cross-context shared tables.
- Treat indexes as write-cost tradeoffs, not free optimizations.
- Use measurements and query plans before physical tuning.

## Output

Use `data-model-design.md` and optionally `erd-html-diagrams`.

## Avoid

- Designing from screens alone.
- One table per class by reflex.
- Generic entity-attribute-value models without a proven need.
- Destructive migrations without compatibility stages.
