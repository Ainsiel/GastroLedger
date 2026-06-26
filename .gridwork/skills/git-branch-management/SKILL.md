# Git Branch Management Skill

## Purpose

Prepare safe Git actions and execute only the specifically approved local action. Keep remote publication and merge under separate gates.

## Read-Only Discovery

Use only the active policy and summarize:

```text
git status --short --branch
git branch --show-current
git diff --stat
git diff --name-only
git log --oneline
```

Do not treat read access as permission to write.

## Procedure

1. Confirm the repository, active branch, approved scope and work order.
2. Check for unrelated user changes and preserve them.
3. Prepare `git-action-plan.md` before any write.
4. List exact files proposed for staging; never use broad staging without explicit approval.
5. Ask separately for branch creation, staging/commit, push and PR creation.
6. Execute only the approved action and record a concise result.
7. Execute a merge only inside `feature-pr-delivery` or `release-promotion` after the exact strong gate.

## Branch Rules

Preferred branch:

```text
feature/<issue-number>-<short-slug>
```

Without an issue:

```text
feature/<run-short-id>-<short-slug>
```

Feature branches start from and target `develop`. Release PRs start from `develop` and
target `main`. Do not push directly to `main` or `develop`.

## Gates

```text
create local branch = approval
stage exact files = approval
local commit = approval
push branch = separate approval
create PR = separate approval
merge to develop/main = separate strong approval in an authorized workflow
```

## Forbidden

- Do not run destructive Git commands.
- Do not discard or rewrite user changes.
- Do not amend, rebase, force push or delete branches without a new explicit gate.
- Do not combine commit, push and PR approval.
- Do not create or push release tags; use `gridwork-release-publisher`.
