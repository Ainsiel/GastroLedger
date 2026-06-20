# Recommended Implementation Order

## Delivery Sequence

Current state: GL-001 through GL-010 are complete in `develop`. GL-011 is the next
recommended dependency-unlocked ready candidate; GL-012 through GL-016 and GL-018
through GL-020 are also ready.

| Order | Issue | Why At This Point |
|---:|---|---|
| 1 | GL-001 | Proves the multi-tenant security and full-stack tracer |
| 2 | GL-002 | Establishes authorization and branch-scoped actors |
| 3 | GL-003 | Establishes operational tenant scope |
| 4 | GL-004 | Creates the catalog needed by recipes and procurement |
| 5 | GL-005 | Creates supplier offers needed by receipt and ordering |
| 6 | GL-006 | Establishes immutable approved recipe versions |
| 7 | GL-007 | Produces active menu items and visible margin |
| 8 | GL-008 | Proves PostgreSQL jobs, outbox and cost projections |
| 9 | GL-009 | Proves receipt atomicity and immutable stock truth |
| 10 | GL-010 | Proves lot conversion and yield |
| 11 | GL-011 | Proves multi-step inventory movement |
| 12 | GL-012 | Adds governed stock reduction |
| 13 | GL-013 | Proves worker-generated in-app alerts |
| 14 | GL-014 | Proves blind count and approval separation |
| 15 | GL-015 | Proves bounded CSV, recipe consumption and exceptions |
| 16 | GL-016 | Establishes manually governed ordering holds |
| 17 | GL-017 | Completes approved purchasing workflow |
| 18 | GL-018 | Completes operational supplier returns |
| 19 | GL-019 | Adds non-payment cash reconciliation |
| 20 | GL-020 | Adds non-payroll workforce records |
| 21 | GL-021 | Adds non-financial royalty estimates from trusted sales |
| 22 | GL-022 | Reconciles trusted source facts into analysis |
| 23 | GL-023 | Proves complete local data exit |

## Parallelism After The Tracer

After `GL-003` is accepted, limited parallel delivery is possible:

- Menu stream: `GL-004 -> GL-006 -> GL-007 -> GL-008`.
- Procurement/inventory stream after `GL-005`: `GL-009` and then its dependents.
- Supporting operations: `GL-016`, `GL-019` and `GL-020`.

Parallel work must still avoid simultaneous incompatible edits to shared application
contracts, migrations or API transport contracts.
