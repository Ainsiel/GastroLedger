# GastroLedger Backlog Drafts

```text
status = published and locally reconciled
github_issues_published = true
generated_on = 2026-06-14
workflow = backlog-management
```

This backlog translates the approved SDD and architecture into observable vertical
slices suitable for TDD delivery. It is grounded in the current repository
foundation and was published to GitHub after explicit approval.

## Outputs

- `backlog-snapshot.md`: normalized backlog and readiness.
- `dependencies.md`: dependency graph and sequencing constraints.
- `implementation-order.md`: recommended delivery order.
- `work-order-candidates.md`: proposed implementation work orders.
- `architecture-traceability.md`: approved architecture evidence per draft.
- `pre-publication-review.md`: validation evidence and resolved findings.
- `publication-manifest.md`: stable local draft to GitHub issue linkage.
- `publication-commands.ps1`: exact GitHub CLI write commands, not yet executed.
- `publication-plan.md`: governed GitHub label and issue publication plan.
- `issues/`: one local GitHub issue draft per vertical slice.

## Draft Contract

Every issue:

- owns one observable outcome;
- identifies one primary bounded context where possible;
- traces approved requirements, use cases and test cases;
- includes frontend, API, domain, persistence and test scope when applicable;
- states exclusions, dependencies, acceptance criteria and definition of done;
- excludes payments, subscriptions, accounting, payroll and external APIs;
- uses only labels from `.gridwork/policies/github-labels.json`.

The initial tracer slice is `GL-001`, tenant registration with a scoped local
session and proven tenant isolation.
