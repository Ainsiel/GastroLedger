# Spring Boot CI Quality Gates

## Purpose

Define reproducible Spring Boot quality gates.

## Procedure

1. Confirm backend path and committed Maven or Gradle wrapper.
2. Read project-defined format and static-analysis tasks.
3. Map unit, integration and package-build commands.
4. Define Java and dependency-cache inputs.
5. Run confirmed commands locally when feasible.
6. Separate fast feature checks from full release checks.
7. Record stable component-check evidence.

## Evidence

- Record wrapper, Java version, commands and outputs.
- Record missing or intentionally skipped checks.

## Guardrails

- Do not call an uncommitted global build tool.
- Do not skip full release integration checks.
- Do not generate during Gridwork installation.
