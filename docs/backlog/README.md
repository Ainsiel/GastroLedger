# GastroLedger Backlog Drafts

```text
status = local drafts only
github_issues_published = false
generated_on = 2026-06-14
workflow = backlog-management
```

This backlog translates the approved SDD and architecture into observable vertical
slices suitable for TDD delivery. It is grounded in the current repository
foundation and contains no GitHub writes.

## Outputs

- `backlog-snapshot.md`: normalized backlog and readiness.
- `dependencies.md`: dependency graph and sequencing constraints.
- `implementation-order.md`: recommended delivery order.
- `work-order-candidates.md`: proposed implementation work orders.
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
