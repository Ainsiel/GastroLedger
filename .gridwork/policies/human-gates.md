# Human Gates Policy

## Always Stop Before

- AFK delegation.
- GitHub write commands.
- Branch push, PR creation, merge or release creation.
- Publishing a PR review, deleting a feature branch, production approval and rollback.
- Local branch creation, staging and commit when proposed by an agent.
- Creating or editing GitHub labels.
- Consequential architecture decisions and promotion of architecture drafts to approved docs.
- Architecture foundation plan approval and product-structure writes.
- Dependency changes.
- Infrastructure file creation or modification outside an approved work order.
- Performance or load testing against shared environments.
- Secret access.
- Destructive file operations.
- Deploy.
- Expanding scope beyond the work order.
- Running a command outside an allowlist.

## Gate Record

When a run exists, record gates in:

```text
.factory/runs/<run-id>/gates.json
.factory/runs/<run-id>/summary.md
```

## Approval Shape

Approval must name the action, scope and target. Broad approval does not authorize unrelated side effects.
