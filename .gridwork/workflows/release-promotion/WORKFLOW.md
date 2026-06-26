# Release Promotion Workflow

## Purpose

Promote a reviewed release candidate through:

```text
develop -> release PR -> full CI -> main -> production deployment
```

## Procedure

1. Confirm source is `develop`, target is `main`, and release scope is known.
2. Prepare included work orders, release notes and a release PR plan.
3. Request approval to create the release PR.
4. Wait for `release / full-regression-gate`, including full unit, integration, architecture,
   regression, end-to-end, migration and production-build checks when applicable.
5. Block promotion when checks fail; return failures to the responsible work stream.
6. Request explicit production approval only after release CI and review pass.
7. Merge to `main` through a separate strong gate.
8. Observe the production environment deployment and smoke checks.
9. Request rollback approval when deployment verification fails.
10. Produce a release promotion report.

Feature branches must never target `main`. Deployment must use the SHA merged to `main`.
