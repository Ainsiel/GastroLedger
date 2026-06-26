# GitHub Actions Reusable Workflows

## Purpose

Extract repeated component checks and builds behind `workflow_call`.

## Procedure

1. Identify repeated jobs across feature, develop and release workflows.
2. Define explicit reusable workflow inputs and outputs.
3. Keep component commands behind root quality contracts.
4. Pass secrets only when strictly required.
5. Keep permissions minimal and explicit.
6. Pin third-party actions according to security policy.
7. Validate every caller and required output.

## Evidence

- Produce reusable workflow contracts.
- Record callers, inputs, outputs and permissions.
- Record action versions and trust decisions.

## Guardrails

- Do not expose user-controlled text directly as shell commands.
- Do not duplicate release-critical logic in callers.
- Do not broaden inherited secrets or permissions.
