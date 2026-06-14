# Pull Request Lifecycle Skill

## Procedure

1. Validate head, base, scope, current SHA and required checks.
2. Require `feature/* -> develop` or `develop -> main`.
3. Prepare title, body, work-order/release references and verification expectations.
4. Request approval before `gh pr create`.
5. Track PR URL, number, base, head and latest head SHA.
6. Keep failed-CI PRs open and blocked.
7. Invalidate approvals after every corrective push.
8. Merge only after required CI, review and exact merge approval.
9. Record merge SHA and strategy.

## Merge Rules

- Feature PRs use squash merge into `develop`.
- Release PRs use merge commit into `main`.
- Never merge a stale, failing or pending SHA.
- Never treat PR creation approval as merge approval.

## Evidence

Record conversations, required checks, approvals, reviewed SHA and merge result without
including secrets.
