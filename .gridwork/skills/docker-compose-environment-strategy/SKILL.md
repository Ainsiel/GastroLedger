# Docker Compose Environment Strategy

## Purpose

Design Compose environments for local development and isolated integration testing.

## Procedure

1. Identify required services and environment-specific differences.
2. Define one base Compose file for shared service contracts.
3. Define development, QA and production-like overlays.
4. Reserve profiles for optional tools and one-shot services.
5. Add readiness health checks and dependency conditions.
6. Define external secret injection without secret values.
7. Validate every supported file combination.

## Evidence

- Produce a Compose environment contract.
- Record supported commands and profiles.
- Record ports, volumes, networks and health checks.

## Guardrails

- Do not use profiles as the only environment separation.
- Do not commit production secret values.
- Do not claim Compose is the production orchestrator unless approved.
