# Module Boundary Enforcement Skill

## Procedure

1. Translate approved dependency rules into observable architecture-test assertions.
2. Test meaningful boundaries such as domain independence, context ownership and
   forbidden cross-module imports.
3. Prefer tests against compiled metadata, imports or public module surfaces.
4. Confirm the test fails when a representative forbidden dependency is introduced
   only when that controlled check is approved.
5. Run approved architecture tests and record evidence.

Do not invent new dependency rules while writing tests.

## Test Selection

Prioritize rules that protect costly architectural decisions:

- domain independence from frameworks;
- bounded-context ownership;
- allowed dependency direction;
- public module surfaces;
- forbidden infrastructure imports.

## Evidence

Record tested rules, command results and uncovered boundaries.

## Gates

Stop when a test requires a new dependency, an unapproved rule or a command outside
the allowlist.
