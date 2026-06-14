# Delivery Infrastructure Workflow

## Purpose

Materialize the approved branch and CI/CD policy as reusable GitHub Actions and reviewed GitHub configuration plans.

## Phases

1. Map root quality commands to reusable component workflows.
2. Create feature PR, develop integration, release PR and production deployment workflows.
3. Require a stable aggregate check for each protected branch.
4. Validate workflow syntax, Compose configuration and container builds locally where possible.
5. Draft rulesets and environments; apply them with `gh` only after explicit approval.

## Required Checks

```text
feature / regression-gate
develop / integration-gate
release / full-regression-gate
production / smoke-gate
```
