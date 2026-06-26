# Changed Scope Detection

## Purpose

Map changed monorepo paths to the checks required for a feature PR.

## Procedure

1. Read the approved component ownership map.
2. Collect changed paths for the current PR head SHA.
3. Map direct component changes to component checks.
4. Expand shared contracts to every dependent component.
5. Expand migrations, Compose, root tooling and CI changes broadly.
6. Produce the affected-component and required-check sets.
7. Compare the result with protected-branch requirements.

## Evidence

- Record changed paths and matched ownership rules.
- Record affected components and required checks.
- Explain every skipped component.

## Guardrails

- Use this optimization only for feature PRs.
- Never skip full release regression.
- Default to broader checks when ownership is ambiguous.
