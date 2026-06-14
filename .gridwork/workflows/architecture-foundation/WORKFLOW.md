# Architecture Foundation Workflow

## Purpose

Convert approved architecture into a minimal executable and enforceable foundation
before functional backlog tasks are implemented.

## Preconditions

- Architecture, ADRs, bounded contexts and dependency rules are approved.
- The stack and target paths are confirmed.
- The exact foundation plan and command allowlist are approved.

## Phases

1. Read approved architecture outputs and identify only decisions ready to materialize.
2. Use `architecture-foundation-planning` to produce an exact file, contract and test plan.
3. Reject speculative abstractions and return architecture ambiguities to `software-architect`.
4. Stop for foundation-plan and product-structure-write approval.
5. Use `project-scaffolding` to create the minimum project and module structure.
6. Use `contract-first-boundaries` only for confirmed boundaries needed by the first slices.
7. Use `composition-root-wiring` for minimal executable assembly.
8. Use `module-boundary-enforcement` and integration testing skills to protect dependency rules.
9. When Next.js is approved, materialize route groups, layouts, public feature surfaces,
   API-client boundary and auth/session boundaries without functional screens.
10. Run approved compile, startup and test commands.
11. Use `architecture-conformance-verification` and produce a conformance report.
12. Use `backlog-planning` to prepare the first functional vertical slices.
13. Hand the foundation to `implementer-agent`; business behavior begins in `tdd-implementation`.

## Forbidden Foundation Output

```text
business rules
complete CRUD implementations
repository adapter behavior
future module placeholders
ports without confirmed consumers
mock behavior presented as production behavior
```

## Human Gates

Stop before foundation writes, dependency or architecture changes, scope expansion,
unknown commands, infrastructure writes, Git/GitHub actions, secrets or destructive
operations.

## Completion Criteria

The approved structure exists, starts or compiles through approved commands,
architecture tests pass, conformance is documented, and no business behavior was
implemented.
