# Architecture Foundation Policy

## Goal

Materialize approved architectural decisions without pre-implementing product behavior
or creating speculative abstractions.

## Allowed Foundation Work

- Confirmed project and module structure.
- Minimal framework bootstrap and composition root.
- Required boundary contracts with known consumers.
- Architecture and dependency-boundary tests.
- Minimal startup or health behavior needed to prove assembly.
- Backlog inputs and handoffs for functional vertical slices.

## Forbidden Foundation Work

- Business rules or user-facing feature behavior.
- Generic CRUD, complete adapters or repository implementations.
- Interfaces, methods, modules or extension points for hypothetical future needs.
- New architectural decisions not recorded in approved architecture or ADRs.
- Dependency or infrastructure changes without explicit approval.

## Contract Test

Every generated abstraction must name:

```text
approved architecture source
known consumer or first slice
boundary protected
reason it must exist before behavior implementation
```

If any field is missing, defer the abstraction to the relevant TDD work order.
