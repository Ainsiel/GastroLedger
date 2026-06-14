# Monorepo Layout Design

## Purpose

Define repository boundaries, ownership and dependency direction before scaffolding.

## Procedure

1. Read the approved architecture and selected deployable components.
2. Identify independently buildable, testable and deployable boundaries.
3. Map each boundary to a confirmed top-level path.
4. Define locations for integration tests, end-to-end tests and infrastructure.
5. Record shared contracts and their allowed consumers.
6. Record ownership and required cross-component checks.
7. Validate that paths do not imply accidental coupling.

## Evidence

- Produce an approved repository layout.
- Produce a component ownership map.
- Record unresolved path decisions.

## Guardrails

- Treat paths as approved decisions, not universal conventions.
- Do not create directories before the write gate.
- Do not place business behavior in shared infrastructure folders.
