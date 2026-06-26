# CI Failure Repair Workflow

## Purpose

Turn failed CI into a reproducible, scoped repair loop without letting verifier evidence drift from the current commit.

## Phases

1. Confirm PR and current head SHA.
2. Read check status, failed job logs and available artifacts with `gh`.
3. Classify the failure as product, test, infrastructure, flaky or policy failure.
4. Reproduce locally when feasible and hand the smallest repair scope to the owning implementer.
5. After a corrective push, discard old evidence and evaluate the new SHA.
6. Return to verifier only when every required check for the current SHA is green.
