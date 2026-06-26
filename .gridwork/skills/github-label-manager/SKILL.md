# GitHub Label Manager Skill

## Purpose

Audit GitHub labels against the installed predefined catalog and prepare a controlled plan for missing labels.

## Rules

- Treat `policies/github-labels.json` as the source of truth.
- Never invent labels from free text.
- Read remote labels only when the active workflow and GitHub CLI policy permit it.
- Prepare a local plan before any GitHub write.
- Require approval before creating or editing labels.
- Do not delete labels in v1.

## Procedure

1. Read the local catalog and validate each required issue draft label.
2. Optionally list remote labels using governed read-only GitHub CLI.
3. Classify labels as present, missing, mismatched or unknown.
4. Block issue publication when a draft references an unknown label.
5. Write a missing-label plan with exact name, color, description and command intent.
6. Ask for approval for the exact create/edit batch.
7. Record the sanitized result in a local apply report.

## Outputs

```text
.factory/runs/<run-id>/artifacts/github-labels/label-audit.md
.factory/runs/<run-id>/artifacts/github-labels/missing-label-plan.md
.factory/runs/<run-id>/artifacts/github-labels/label-apply-report.md
```

## Forbidden

- Do not create labels without approval.
- Do not use labels outside the installed catalog.
- Do not delete or rename existing labels automatically.
- Do not publish issues merely because labels were prepared.
