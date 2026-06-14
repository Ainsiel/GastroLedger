# Frontend Architecture Design Skill

## Procedure

1. Map user workflows to frontend features and route ownership.
2. Separate route composition, feature behavior, entities and shared primitives.
3. Define public module surfaces and allowed dependency direction.
4. Keep backend authorization and domain truth outside the frontend.
5. Identify cross-feature coordination that requires an explicit contract.
6. Define loading, empty, error, unauthorized and stale-state ownership.
7. Produce frontend architecture and dependency rules.

## Rules

- Organize around user capabilities, not only technical layers.
- Do not mirror backend DDD layers mechanically.
- Do not create a shared module for code used only once.
- Prevent imports into feature internals through architecture tests when materialized.

## Verification

Review route ownership, feature boundaries, public imports, shared-code justification
and consistency with visible user workflows.

## Output

Record features, owned routes, public entry points, allowed dependencies, shared
primitives, cross-feature contracts and unresolved decisions.

## Gates

Stop before changing public boundaries, assigning ambiguous ownership or introducing a
shared abstraction without confirmed consumers.

## Blocking Conditions

Block when user workflows, backend contracts or frontend scope are too uncertain to
assign boundaries safely.
