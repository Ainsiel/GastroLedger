# Next.js CI Quality Gates

## Purpose

Define reproducible Next.js checks for local and CI execution.

## Procedure

1. Confirm frontend path, lockfile and package manager.
2. Read scripts from `package.json`.
3. Map lint, typecheck, unit-test and build commands.
4. Define cache inputs from the lockfile.
5. Define environment inputs without secret values.
6. Run every confirmed command locally when feasible.
7. Publish stable component-check evidence.

## Evidence

- Record commands, versions and outputs.
- Record missing or intentionally skipped gates.

## Guardrails

- Do not invent scripts outside approved bootstrap.
- Do not treat a development build as production validation.
- Do not expose secrets through public build variables.
