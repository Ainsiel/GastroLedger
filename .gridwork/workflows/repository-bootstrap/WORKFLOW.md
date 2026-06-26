# Repository Bootstrap Workflow

## Purpose

Create the approved technical skeleton before business work orders are delegated.

## Phases

1. Confirm stack, repository boundaries and deployment assumptions from approved architecture.
2. Create only stack scaffolds, module boundaries, root commands, containers and test harness foundations.
3. Create base Compose plus development, QA and production overlays; reserve profiles for optional services.
4. Validate dependency installation, build, Compose configuration and empty baseline tests.
5. Record commands and hand off to `delivery-infrastructure`.

## Guardrail

Scaffolding may expose health checks and placeholders required to prove wiring, but must not implement business behavior.
