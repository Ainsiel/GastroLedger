# Recovery And Rollback Plan

```text
rpo = 15 minutes
rto = 4 hours
deployment_strategy = immutable artifacts with backward-compatible migrations
```

## Data Recovery

- Daily encrypted full PostgreSQL backup plus continuous WAL archiving.
- Scheduled restore rehearsal validates tenant isolation, ledger totals and critical
  workflows.
- Recovery smoke checks cover registration/session, recipe lookup, balance query,
  receiving, sales import status and report confidence.

## Deployment Rollback

- Keep the previous trusted web/API/worker artifacts deployable during the rollback
  window.
- Use expand/migrate/contract schema changes.
- Prefer roll-forward when reverting would discard accepted inventory transactions.
- Destructive migrations require separate approval and verified recovery procedure.

## Trigger Conditions

Rollback or roll-forward decision is required for tenant isolation failure, ledger
integrity failure, broad authentication outage or migration incompatibility.
Performance degradation without correctness risk may use controlled roll-forward.
