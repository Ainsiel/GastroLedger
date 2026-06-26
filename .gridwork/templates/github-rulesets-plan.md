# GitHub Rulesets Plan

## Develop

- Require pull request and `feature / regression-gate`.
- Require verifier approval for the latest push.
- Dismiss stale approvals and resolve conversations.
- Block direct pushes, force pushes and deletion.

## Main

- Require `develop -> main` release PR and `release / full-regression-gate`.
- Require production approval and resolved conversations.
- Block direct pushes, force pushes, deletion and bypass.

## Feature Branches

- Match `feature/**`.
- Block force pushes.
- Allow deletion only after approved merge.
