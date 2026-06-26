# CI Status Evaluation Skill

## Procedure

1. Confirm PR number, exact head SHA and required check names.
2. Use governed reads such as `gh pr checks`, `gh run list` and `gh run view`.
3. Classify each check as pending, success, failed, cancelled, skipped or unknown.
4. Require the configured aggregate gate for the current SHA.
5. When checks fail, keep the PR open and produce a concise failure handoff.
6. Route corrective work to the implementer without inventing a fix.
7. After a new push, mark previous evidence and verifier approval stale.
8. Permit verifier review only when required checks succeed.

## Decisions

```text
ci_pending
ci_failed
ci_passed
ci_unknown
```

## Gates

Reruns and any GitHub write require approval. Never report success for a different SHA,
missing required check or ambiguous job name.
