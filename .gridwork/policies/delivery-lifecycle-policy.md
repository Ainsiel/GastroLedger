# Delivery Lifecycle Policy

## Branch Model

```text
main = production
develop = integration
feature/<work-order-id>-<slug> = one approved work order
```

Feature branches start from `develop` and target `develop`. Release PRs start from
`develop` and target `main`. Direct pushes to `develop` and `main` are forbidden.

## Required Order

```text
local checks -> commit -> push -> PR -> CI -> verifier -> merge
```

The verifier may approve only the exact PR head SHA with successful required checks.
Every corrective push makes previous CI evidence and verifier approval stale.

## CI Failure

A failed check keeps the PR open and blocked. Record `ci_failed`, hand actionable
failures to the implementer, and repeat checks after a corrective push.

## Merge Strategy

Use squash merge for `feature/* -> develop`. Use a merge commit for
`develop -> main`. Merge, branch deletion, production approval, deployment and rollback
remain separate human gates.
