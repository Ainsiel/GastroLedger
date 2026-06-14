# PostgreSQL Performance Skill

## Purpose

Improve PostgreSQL performance from representative queries, plans and workload evidence.

## Procedure

1. Define the slow or high-cost query scenario and expected result.
2. Capture duration, frequency, row counts and representative parameters.
3. Inspect the execution plan using a safe approved environment.
4. Determine whether cost is caused by query shape, missing/selectivity-poor index, statistics, locking, data volume or connection pressure.
5. Propose the smallest safe change.
6. Measure read improvement and write/storage cost.
7. Validate correctness and record migration/rollback implications.

## Guidance

- Select indexes from real predicates, joins, ordering and selectivity.
- Prefer keyset pagination for large frequently paged ordered datasets.
- Avoid fetching unused columns or unbounded result sets.
- Keep statistics healthy and recognize stale estimates.
- Check lock waits and transaction age before blaming query execution.
- Use partial, covering or expression indexes only for a demonstrated workload.
- Keep connection counts bounded; more connections can reduce throughput.
- Treat denormalization and materialized views as explicit consistency tradeoffs.

## Evidence

Record sanitized:

```text
query shape
representative parameters
before and after plan summary
before and after timing
rows and buffers when safely available
write/storage tradeoff
```

## Forbidden

- Do not use production data or run intrusive analysis without approval.
- Do not add indexes by guesswork.
- Do not disable correctness constraints for speed.
- Do not treat one cold run as a reliable benchmark.
