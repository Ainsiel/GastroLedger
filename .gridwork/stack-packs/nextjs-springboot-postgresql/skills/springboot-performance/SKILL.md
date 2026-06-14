# Spring Boot Performance Skill

## Purpose

Measure and improve Spring Boot latency, throughput and resource use without speculative tuning.

## Procedure

1. Define workload, percentile target, concurrency and correctness conditions.
2. Capture a repeatable baseline with representative data.
3. Observe application, JVM, database and downstream timings.
4. Rank bottleneck hypotheses.
5. Optimize one measured bottleneck.
6. Re-run the same workload and regression checks.
7. Record gains, resource cost and failure behavior.

## Investigation Order

Prefer investigating:

1. slow or excessive database queries;
2. external call latency and retry behavior;
3. transaction scope and lock contention;
4. serialization and oversized payloads;
5. thread or connection pool saturation;
6. cache opportunities with safe invalidation;
7. allocation, garbage collection and JVM tuning.

## Guidance

- Fix N+1 queries and unnecessary fetches before adding caches.
- Keep database and HTTP pools bounded and aligned with downstream capacity.
- Keep transactions short and avoid remote calls inside them.
- Use async work only when ownership, failure, backpressure and observability are defined.
- Add caching only with explicit key, TTL, invalidation and consistency semantics.
- Expose safe health and metrics signals without leaking sensitive data.
- Use timeouts and bounded retries at external boundaries.

## Forbidden

- Do not tune JVM flags without measurements.
- Do not increase pools to hide downstream saturation.
- Do not add caching that changes correctness silently.
- Do not run load tests against shared or production environments without approval.
