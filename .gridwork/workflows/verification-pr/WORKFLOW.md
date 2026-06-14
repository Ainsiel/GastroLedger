# Verification PR Workflow

## Purpose

Review the current PR head after required CI passes, then approve it for governed merge
or return actionable findings to the implementer.

## When To Use

Use this workflow after `tdd-implementation`, or when the user asks for review of a PR or implementation.

## When Not To Use

Do not use this workflow to fix code directly, publish issues, merge, deploy or replace CI.

## Participating Agents

```text
primary_agent = verifier-agent
supporting_agents = orchestrator,implementer-agent
mode = assisted
```

## Allowed Skills

```text
github-cli
github-issue-discovery
diagnose-bug
tdd
integration-test-design
integration-testing
architecture-conformance-verification
git-branch-management
pull-request-lifecycle
ci-status-evaluation
conditional stack-pack skills
handoff
```

## Phases

1. Confirm the PR, current head SHA and successful required CI checks.
2. Block with `blocked_by_ci` when checks are pending, failing, stale or unknown.
3. Read work order, acceptance criteria and implementation summary.
4. Use `tdd` in assessment mode to review red, green and refactor evidence.
5. Inspect changed files and path scopes.
6. Run allowlisted checks when allowed.
7. Use `architecture-conformance-verification` when architecture or foundation boundaries are in scope.
8. When frontend scope exists, review feature ownership, route/server-client boundaries,
   state ownership, API/error behavior, auth boundaries, cache semantics, accessibility and tests.
9. Produce a local verifier report.
10. Prepare a gated GitHub review only if requested.
11. Decide `pass`, `changes_requested`, `needs_more_evidence`, `blocked_by_ci` or `blocked_by_branch_state`.
12. After `pass`, hand the exact approved SHA back to `feature-pr-delivery`.

Use relevant stack skills in review mode. A performance improvement cannot pass without comparable before/after evidence; infrastructure changes cannot pass without configuration and lifecycle validation.

## Human Gates

Stop before `gh pr comment`, merge, deploy, branch push or code modification.

Creating a local commit, pushing a branch, creating a PR, publishing review and merging require separate approvals.

## Artifacts

```text
.factory/runs/<run-id>/artifacts/verification/verifier-report.md
.factory/runs/<run-id>/artifacts/verification/github-pr-comment.md
.factory/runs/<run-id>/artifacts/git/git-action-plan.md
```

## Completion Criteria

The workflow can close when the current CI-green SHA has a clear verification decision
and any feedback to `implementer-agent` is documented.
