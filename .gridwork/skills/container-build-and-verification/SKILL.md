# Container Build And Verification

## Purpose

Build and verify deterministic runtime containers without publishing by default.

## Procedure

1. Read the approved runtime and container contract.
2. Inspect build context, ignore rules and dependency locks.
3. Build the image with the approved command.
4. Inspect runtime user, entrypoint and exposed ports.
5. Start the image in an isolated test environment.
6. Execute health and smoke checks.
7. Record image identity, size and verification output.

## Evidence

- Produce a container verification report.
- Record build inputs and resulting image identity.
- Record startup, health and smoke-check results.

## Guardrails

- Keep secrets out of image layers and logs.
- Prefer non-root runtime users and minimal final stages.
- Do not publish images or deploy without approval.
