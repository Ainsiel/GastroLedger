# FastAPI Performance Skill

## Purpose

Measure and improve FastAPI latency, throughput and resource use while preserving
correctness, isolation and operational clarity.

## Procedure

1. Define the endpoint or workload, percentile target, concurrency and correctness conditions.
2. Capture a repeatable baseline with representative sanitized data.
3. Observe application, event-loop, database and downstream timings.
4. Rank bottleneck hypotheses before changing code.
5. Change one measured bottleneck at a time.
6. Repeat the same workload and integration checks.
7. Record gains, resource cost, regressions and failure behavior.

## Investigation Order

Prefer investigating:

1. slow or excessive database queries;
2. blocking sync work inside async request paths;
3. downstream latency, retries and timeouts;
4. serialization and oversized payloads;
5. connection pool and worker saturation;
6. unnecessary middleware or dependency work;
7. caching opportunities with safe invalidation.

## Guidance

- Match async libraries and drivers to actual concurrency needs.
- Do not convert code to async without verifying that dependencies are non-blocking.
- Keep database and HTTP pools bounded and aligned with downstream capacity.
- Use multiple workers only with clear deployment and resource assumptions.
- Add caching only with explicit keys, TTL, invalidation and authorization safety.
- Keep timeouts and retries bounded at external boundaries.
- Measure startup and lifespan resource behavior when it affects availability.

## Evidence

Record sanitized before/after latency, throughput, errors, resource use and the
approved workload shape.

## Forbidden

- Do not optimize without a baseline.
- Do not run load tests against shared or production environments without approval.
- Do not increase workers or pools to hide downstream saturation.
- Do not add performance dependencies without approval.

