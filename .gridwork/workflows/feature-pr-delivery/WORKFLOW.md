# Feature PR Delivery Workflow

## Purpose

Deliver exactly one approved work order through:

```text
develop -> feature/<work-order-id>-<slug> -> PR -> CI -> verifier -> develop
```

## Procedure

1. Confirm the feature branch was created from `develop` for one work order.
2. After implementation passes local checks, separately gate commit, push and PR creation.
3. Create the PR with base `develop` and record its head SHA.
4. Use `ci-status-evaluation` to wait for `feature / regression-gate`.
5. When CI fails, keep the PR open, mark `ci_failed` and hand failures to the implementer.
6. After corrective pushes, invalidate old CI and verifier evidence and repeat.
7. Delegate final review to `verification-pr` only when required checks pass for the current SHA.
8. When verifier requests changes, return findings to the implementer and repeat CI.
9. After CI and verifier pass, request a separate `merge_to_develop` gate.
10. Squash merge to `develop` and optionally delete the feature branch after approval.

## Completion

Close only after merge into `develop`, or with a documented blocking state. Never
close a PR merely because CI failed.
