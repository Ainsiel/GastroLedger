# Composition Root Wiring Skill

## Procedure

1. Identify the approved application entry point and components that must be assembled.
2. Keep construction and framework dependency injection outside domain modules.
3. Wire only components required to prove the foundation starts.
4. Use explicit failing or unavailable adapters instead of fake production behavior.
5. Verify assembly through approved startup or smoke commands.

Do not implement adapter behavior or hide unresolved dependencies behind mocks.

## Assembly Rules

- Keep the composition root replaceable and outside domain modules.
- Wire only approved components.
- Make missing production adapters explicit.
- Keep test-only wiring out of production assembly.

## Evidence

Record entry point, assembled components, deferred adapters and startup command result.

## Gates

Stop before dependencies, infrastructure changes, new architecture decisions or
unapproved component wiring.
