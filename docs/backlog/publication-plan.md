# GitHub Issue Publication Plan

```text
status = published and reconciled
approved = true
repo = Ainsiel/GastroLedger
remote_writes_performed = true
```

## Read-Only Audit

- Existing GitHub issues: `0`.
- Existing approved Gridwork labels: `0`.
- GitHub currently contains only default repository labels.

## Exact Write Set

`publication-commands.ps1` is the exact proposed GitHub CLI command set:

- create four labels from `.gridwork/policies/github-labels.json`;
- publish 23 issues in dependency-respecting implementation order;
- apply `status:ready` only to the initial tracer, GL-001.

The publication approval is a single gate covering those 27 writes. No command
assigns a work order, creates a branch, commits, pushes, opens a PR or changes any
other repository setting.

## Reconciliation After Approval

1. Execute the commands from the repository root.
2. Capture each returned issue URL in command order.
3. Replace each `pending` value in `publication-manifest.md`.
4. Read back all published issues and labels.
5. Generate the final backlog snapshot with publication counts and URLs.

The approved command set was executed once on 2026-06-14. GitHub returned issues
`#1` through `#23`; titles and labels were read back and reconciled successfully.
