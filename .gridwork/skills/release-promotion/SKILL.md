# Release Promotion Skill

## Procedure

1. Confirm `develop` source SHA, `main` base SHA and included work orders.
2. Verify no feature branch is targeting `main`.
3. Prepare release scope, compatibility notes and release PR body.
4. Request approval before creating `develop -> main` PR.
5. Require the full `release / full-regression-gate` on the exact head SHA.
6. Summarize release findings and unresolved risks.
7. Request explicit production approval and separate merge approval.
8. Record merge SHA and hand off to deployment verification.

## Blocking Conditions

Block on failed or missing CI, unknown included work, unresolved review findings,
unapproved migrations, or stale release evidence.

## Release Evidence

Record:

- source and target SHAs;
- included work orders;
- release PR URL and reviewed head SHA;
- required check results;
- production and merge approvals;
- merge SHA and deployment handoff.

## Decision

Use `release_ready`, `release_blocked` or `needs_more_evidence`. Never infer production
approval from an earlier feature merge.

## Forbidden

Do not repair product code, bypass checks, push directly to `main`, deploy, or expose
secret values.
