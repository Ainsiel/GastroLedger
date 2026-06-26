# FastAPI CI Quality Gates

## Purpose

Define reproducible FastAPI quality gates.

## Procedure

1. Confirm backend path, Python version and lockfile.
2. Read project-defined formatter, lint and typing tools.
3. Map unit, integration and package-build commands.
4. Define dependency-cache inputs.
5. Run confirmed commands locally when feasible.
6. Separate fast feature checks from full release checks.
7. Record stable component-check evidence.

## Evidence

- Record Python version, commands and outputs.
- Record missing or intentionally skipped checks.

## Guardrails

- Do not invent tools outside approved bootstrap.
- Do not skip full release integration checks.
- Do not generate during Gridwork installation.
