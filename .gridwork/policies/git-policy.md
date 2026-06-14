# Git Policy

## Read Actions

Repository inspection may use non-destructive commands allowed by the active agent and workflow:

```text
git status --short --branch
git branch --show-current
git diff --stat
git diff --name-only
git log --oneline
```

## Write Gates

- Creating a local branch requires approval.
- Staging must name exact files and requires approval.
- A local commit requires approval.
- Push and PR creation require separate approvals.
- Merge to `develop` or `main` requires a separate strong approval inside its authorized workflow.

## Protection

- Preserve unrelated user changes.
- Never reset, checkout away, clean, force push, amend or rewrite history without a new explicit gate.
- Never push directly to `main` or `develop`.
- Feature branches must start from `develop`, target `develop` and map to one work order.
- Release PRs must start from `develop` and target `main`.
- Use squash merge for feature PRs and merge commits for release PRs.
- Release tags are governed only by `gridwork-release-publisher`.
