# TDD Implementation Workflow

## Purpose

Implement an approved work order with TDD and leave evidence for verification.

## When To Use

Use this workflow only when an issue or approved work order is ready for AFK delegation.

## When Not To Use

Do not use this workflow for ambiguous requests, architecture design, PR review, issue publishing or deployment.

## Participating Agents

```text
primary_agent = implementer-agent
supporting_agents = orchestrator
mode = afk
```

## Allowed Skills

```text
github-issue-discovery
diagnose-bug
tdd
integration-test-design
integration-testing
git-branch-management
conditional stack-pack skills
handoff
```

## Preconditions

- A work order exists and is approved.
- Acceptance criteria are clear.
- Path scopes are known.
- Test commands are allowlisted.
- Branch policy is clear.

## Phases

1. Read the work order and confirm scope.
2. Validate the work-order contract and command allowlist.
3. Use `tdd` to create a prioritized behavior plan.
4. Define the first red phase before editing product code.
5. Add or update one behavior test through a public interface.
6. Run the narrow allowlisted test and record the expected failing result.
7. Implement the smallest green change.
8. Run the same relevant test and record the passing result.
9. Repeat one vertical behavior cycle at a time.
10. Refactor only while green and without changing behavior.
11. Run final verification commands from the allowlist.
12. Write TDD evidence and handoff to verifier when needed.
13. Correct CI or verifier findings on the same work-order feature branch.
14. Use `git-branch-management` only for an explicitly approved Git action.
15. Hand completed local implementation to `feature-pr-delivery`.

When a work order confirms Next.js, Spring Boot, FastAPI, PostgreSQL or Docker scope, select the smallest relevant stack skill. Use `integration-testing` when behavior must cross real component boundaries. Use performance skills only when the acceptance criteria include a measurable performance problem or target.

## TDD Rule

```text
no_clear_red_phase = block
missing_red_or_green_evidence = needs_more_evidence
```

For fullstack vertical slices, prefer a tracer bullet that crosses the visible user path, API/application boundary, domain behavior and persistence boundary when reasonable.

## Human Gates

Stop before dependency changes, scope changes, unknown commands, destructive operations, branch push, PR creation, deploy or secret access.

Branch creation, staging, commit, push and PR creation are separate gates. Merge is manual in v1.

## Artifacts

```text
.factory/runs/<run-id>/artifacts/tdd/tdd-evidence.md
.factory/runs/<run-id>/artifacts/tdd/tdd-plan.md
.factory/runs/<run-id>/artifacts/implementation-summary.md
.factory/runs/<run-id>/artifacts/git/git-action-plan.md
.factory/runs/<run-id>/artifacts/tdd/command-summary.md
.factory/runs/<run-id>/handoffs/implementer-to-verifier.md
```

## Completion Criteria

The workflow can close when implementation, evidence and local checks are ready for `feature-pr-delivery`.
