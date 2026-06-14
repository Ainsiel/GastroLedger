# C4 HTML Diagrams Skill

## Purpose

Create an optional C4 diagram in self-contained HTML when system boundaries or responsibilities need a visual explanation.

## Level Selection

- Context: people, external systems and the system under design.
- Container: deployable or runnable units, responsibilities and communication.
- Component: major internal modules inside one selected container.
- Dynamic: a focused runtime interaction for one scenario.

Do not mix levels in one diagram. Do not create code-level C4 diagrams by default.

## Procedure

1. State the question the diagram must answer and its audience.
2. Select one C4 level.
3. List included and excluded elements.
4. Validate names, responsibilities, technologies and ownership against approved artifacts.
5. Draw directional relationships with a short purpose and protocol when known.
6. Render using `html-architecture-diagrams` and `diagram-html-policy.md`.
7. Add a textual inventory and relationship table.
8. Validate locally and record assumptions in `diagram-notes.md`.

## Quality Rules

- Every element has a name, type and one-line responsibility.
- External systems remain visibly external.
- Boundaries communicate ownership or deployment, not decoration.
- Proposed elements are visually distinct from approved elements.
- Too many elements means the scope or level must be narrowed.
