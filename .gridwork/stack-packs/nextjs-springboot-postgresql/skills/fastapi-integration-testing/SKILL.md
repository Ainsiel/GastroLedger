# FastAPI Integration Testing

## Purpose

Verify FastAPI behavior across HTTP, persistence and external adapters.

## Procedure

1. Select scenarios from approved acceptance criteria.
2. Identify ASGI, persistence and external boundaries.
3. Start isolated real dependencies where behavior depends on them.
4. Exercise public HTTP behavior.
5. Override external adapters explicitly.
6. Prove fixture and transaction cleanup.
7. Record commands, environment and results.

## Evidence

- Record tested boundaries and scenarios.
- Record dependency versions and failure artifacts.

## Guardrails

- Do not call uncontrolled production services.
- Do not hide persistence behavior behind mocks.
- Do not generate during Gridwork installation.
