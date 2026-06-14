# GitHub Environments Management

## Purpose

Plan and apply approved GitHub deployment environments and protections.

## Procedure

1. Read the approved deployment policy.
2. Inspect existing environments without reading secret values.
3. Define allowed branches or tags for each environment.
4. Define reviewers, wait timers and protection rules.
5. Record required secret names without their values.
6. Present the exact remote change for approval.
7. Apply and verify only after approval.

## Evidence

- Produce a GitHub environments plan.
- Record effective protection and deployment-source rules.
- Record secret names only, never values.

## Guardrails

- Production must require explicit approval.
- Do not read, print or replace secret values.
- Do not apply remote changes without approval.
