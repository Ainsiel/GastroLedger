# Spring Boot Integration Testing

## Purpose

Verify Spring Boot behavior across meaningful real boundaries.

## Procedure

1. Select scenarios from approved acceptance criteria.
2. Identify HTTP, messaging, persistence and external boundaries.
3. Start isolated real dependencies where behavior depends on them.
4. Exercise public interfaces instead of internal implementation.
5. Keep external systems behind explicit test adapters or containers.
6. Prove fixture and transaction isolation.
7. Record commands, environment and results.

## Evidence

- Record tested boundaries and scenarios.
- Record dependency versions and failure artifacts.

## Guardrails

- Do not call uncontrolled production services.
- Do not hide integration behavior behind mocks.
- Do not generate during Gridwork installation.
