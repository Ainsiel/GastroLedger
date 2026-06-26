# PostgreSQL Test Environment

## Purpose

Provide isolated PostgreSQL environments for integration and migration checks.

## Procedure

1. Confirm supported PostgreSQL version and extensions.
2. Create a disposable isolated database service.
3. Add deterministic readiness checks.
4. Apply approved migrations.
5. Seed only explicit test fixtures.
6. Run integration or migration checks.
7. Destroy or reset the isolated environment.

## Evidence

- Record database version, extensions and readiness.
- Record migration and cleanup results.

## Guardrails

- Never point tests at shared development, QA or production data.
- Do not reuse state across independent test runs.
- Do not generate during Gridwork installation.
