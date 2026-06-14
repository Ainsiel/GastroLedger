# Quality Command Contract

## Purpose

Expose stable root commands shared by developers, agents and CI.

## Procedure

1. Detect the existing root task runner and component commands.
2. Define intents for lint, unit, integration, E2E, build and Compose validation.
3. Map each root intent to confirmed component commands.
4. Keep environment setup explicit and deterministic.
5. Ensure CI invokes the same root intents used locally.
6. Run every declared root command.
7. Record unsupported or intentionally skipped intents.

## Evidence

- Produce the root quality-command contract.
- Record command output and runtime assumptions.
- Identify commands requiring external services.

## Guardrails

- Do not invent commands outside approved bootstrap.
- Do not hide failing component commands behind wrappers.
- Keep secrets outside command definitions and logs.
