# Work Order Branch Lifecycle Skill

## Procedure

1. Confirm the exact approved work order and current `develop` reference.
2. Detect existing branches or open PRs for the same work order.
3. Propose `feature/<work-order-id>-<short-slug>`.
4. Confirm the branch represents exactly one work order.
5. Request approval before creating the local branch.
6. Record base SHA, branch name, work-order ID and creation result.
7. Preserve unrelated worktree changes.
8. After merge, request separate approval before deleting the feature branch.

## Invariants

- Base branch is `develop`.
- Target branch is `develop`.
- One feature branch maps to one work order.
- No direct push to `develop` or `main`.
- No force push or history rewrite.

## Blocking Conditions

Stop for duplicate active delivery, unclear base SHA, invalid branch name, scope
expansion or unapproved branch creation/deletion.
