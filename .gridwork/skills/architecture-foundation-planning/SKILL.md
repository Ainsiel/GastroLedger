# Architecture Foundation Planning Skill

## Procedure

1. Read only approved architecture, ADRs, boundaries and stack decisions.
2. List decisions that can be materialized without interpretation.
3. Map each proposed file, contract and test to an approved source.
4. Require a known consumer or first slice for every proposed abstraction.
5. Define the minimum executable structure and explicit exclusions.
6. Separate dependency, infrastructure and architecture decisions into gates.
7. Write `architecture-foundation-plan.md` and request exact approval.

## Rule

Do not plan business behavior, generic CRUD, future modules or speculative extension
points. Return unresolved architectural questions to `software-architect`.

## Required Traceability

For every proposed artifact, record:

- approved architecture source;
- known consumer or first slice;
- exact target path;
- boundary or decision materialized;
- reason it cannot wait for the functional slice.

## Output

Use `architecture-foundation-plan.md`. Mark uncertain items as blocked rather than
silently resolving them.

## Gates

Stop before architecture decisions, dependency changes, scope expansion or foundation
writes.
