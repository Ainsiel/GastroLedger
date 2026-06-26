# UML HTML Diagrams Skill

## Purpose

Create one focused UML-style diagram in self-contained HTML when behavior, lifecycle or structural relationships are difficult to explain in prose.

## Type Selection

- Sequence: ordering, calls, messages, alternatives and failures for one scenario.
- State: allowed lifecycle states, transitions, guards and terminal states.
- Activity: business or operational flow with decisions and parallel work.
- Class/domain: important concepts, responsibilities and relationships, not every implementation class.
- Deployment: runtime nodes, artifacts, networks and trust boundaries.

## Procedure

1. State the architecture question and choose one diagram type.
2. Limit the diagram to one scenario, lifecycle or structural concern.
3. Use ubiquitous language and approved contracts.
4. Include alternate/error behavior where it changes the design.
5. Mark asynchronous, transactional and external interactions clearly.
6. Render using `html-architecture-diagrams`.
7. Add a textual equivalent and validate against source artifacts.

## Avoid

- Mixing several UML types in one canvas.
- Reverse-engineering every class into a diagram.
- Sequence diagrams showing only the happy path when failure behavior is architecturally important.
- State diagrams with transitions not backed by domain rules.
