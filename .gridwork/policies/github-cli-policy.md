# GitHub CLI Policy

GitHub CLI is a governed tool, not a workflow.

## Read Only

Read-only commands may be proposed or executed when allowed by the active agent and workflow:

```text
gh issue view
gh issue list
gh pr view
gh pr list
gh repo view
gh run list
gh run view
gh pr checks
gh label list
```

Record the command summary in runtime tool-call logs when a run exists.

## Writes Require Approval

Commands with external side effects require approval:

```text
gh issue create
gh issue edit
gh issue comment
gh pr create
gh pr comment
gh pr edit
gh pr review
gh label create
gh label edit
```

Prepare the payload first. Do not execute the write until the user approves.

## Strong Gate Or Blocked

These commands require a strong human gate or remain blocked in v1:

```text
gh pr merge
gh release create
gh workflow run
gh secret set
gh repo delete
gh label delete
```

`gh pr merge` is authorized only for an approved `feature-pr-delivery` merge to
`develop` or `release-promotion` merge to `main`. Workflow reruns and dispatches require
their own explicit approval.

## Secrets

Never write token values, secret values or full auth output to `.factory/`, GitHub issues, PR comments or release notes.
