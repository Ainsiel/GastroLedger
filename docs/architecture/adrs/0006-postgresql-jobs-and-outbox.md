# ADR-0006: Use PostgreSQL Jobs And Transactional Outbox

```text
status = proposed
```

## Decision

Use a leased PostgreSQL job table and transactional outbox for cost recalculation,
sales allocation, expiry alerts, notifications and report projections.

## Consequences

- Jobs and consumers must be idempotent and observable.
- Source business transactions do not wait for projection or notification work.
- Queue contention, throughput or isolation failures are review triggers for a
  dedicated broker.
