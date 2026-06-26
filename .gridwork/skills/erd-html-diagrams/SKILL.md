# ERD HTML Diagrams Skill

## Purpose

Create an optional MER or ERD diagram in self-contained HTML for an approved conceptual, logical or physical data model.

## Procedure

1. Select conceptual, logical or physical scope and state it explicitly.
2. Include only entities or relations needed to answer the diagram goal.
3. Show identifiers, ownership and lifecycle where relevant.
4. Show relationship direction, optionality and cardinality.
5. Include important uniqueness and referential constraints.
6. Keep cross-bounded-context relationships visibly separate and contract-based.
7. Render using `html-architecture-diagrams`.
8. Add a textual entity and relationship inventory.

## Rules

- Do not imply foreign keys across independent data ownership boundaries.
- Do not mix domain concepts and physical tables without labeling the level.
- Do not show every column unless physical detail is the purpose.
- Mark unconfirmed cardinality and retention decisions.
- Validate the diagram against `relational-data-modeling` outputs.
