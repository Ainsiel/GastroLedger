# CI Failure Diagnosis

## Purpose

Classify failed required checks and create a reproducible repair handoff.

## Procedure

1. Confirm the PR and current head SHA.
2. Read required-check results, failed job logs and artifacts.
3. Isolate the first meaningful failure.
4. Classify it as product, test, infrastructure, flaky or policy.
5. Reproduce locally with approved commands when feasible.
6. Identify the owning agent and smallest repair scope.
7. Produce a handoff and required rerun list.

## Evidence

- Record failed job, step and relevant log excerpt.
- Record reproduction result and classification.
- Record affected checks and owner.

## Guardrails

- Do not hide flaky failures with blind retries.
- Do not expose secret values from logs.
- Do not modify product code during diagnosis.
