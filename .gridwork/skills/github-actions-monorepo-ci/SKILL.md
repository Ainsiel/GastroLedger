# GitHub Actions Monorepo CI

## Purpose

Design branch-aware CI gates for a multi-component repository.

## Procedure

1. Read the branch delivery policy and root quality commands.
2. Define feature PR, develop, release PR and production events.
3. Define stable aggregate required-check names.
4. Use changed-scope optimization only for feature PRs.
5. Run cross-component checks when shared contracts change.
6. Run the complete regression contract for release PRs.
7. Validate event filters, permissions and failure behavior.

## Evidence

- Produce workflow drafts and a required-check plan.
- Record which checks protect each branch.
- Record path-filter assumptions and full-suite exceptions.

## Guardrails

- Never skip release tests using changed paths.
- Never begin verifier acceptance on stale SHA evidence.
- Do not deploy or write workflows without the required gate.
