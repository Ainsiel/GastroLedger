# Deployment Verification Skill

## Procedure

1. Confirm the deployment corresponds exactly to the SHA merged into `main`.
2. Observe deployment status through governed GitHub reads.
3. Review approved smoke-check and health-check evidence.
4. Distinguish deployment failure from application verification failure.
5. Produce `deployed`, `deployment_failed` or `needs_more_evidence`.
6. Recommend rollback when production safety requires it.
7. Request explicit approval before rollback or workflow dispatch.
8. Record environment name and evidence without secret values.

## Safety Rules

- Do not trigger deployment merely because `main` changed unless the approved pipeline does so.
- Do not read, print or modify environment secrets.
- Do not declare success for a different SHA.
- Do not execute rollback without its own gate.

## Output

Produce deployment verification and rollback recommendation for the release report.

## Evidence

Record the main SHA, workflow run, environment, deployment state, smoke-check result,
failure ownership and any separately approved rollback action.

## Blocking Conditions

Use `needs_more_evidence` when the deployed SHA, environment, smoke checks or workflow
result cannot be confirmed.
