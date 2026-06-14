# Next.js Performance Skill

## Purpose

Measure and improve Next.js performance while preserving correctness, freshness and user experience.

## Procedure

1. Define the user-visible performance scenario and target.
2. Capture a reproducible baseline before changing code.
3. Determine whether cost comes from server work, network, bundle, hydration, rendering, images or third parties.
4. Rank hypotheses and change one variable at a time.
5. Apply the smallest optimization.
6. Re-measure the same scenario and check correctness.
7. Record tradeoffs, especially cache freshness and operational cost.

## Guidance

- Prefer Server Components for non-interactive rendering.
- Minimize client component boundaries and browser JavaScript.
- Avoid sequential data waterfalls when independent work can run concurrently.
- Define caching, revalidation and invalidation from product semantics.
- Keep dynamic rendering only where required.
- Load large or rare client features on demand when it improves the measured scenario.
- Optimize images, fonts and third-party scripts using existing Next.js capabilities.
- Watch serialization size across server/client boundaries.
- Use stable keys and avoid unnecessary rerenders.

## Evidence

Capture relevant measures such as:

```text
LCP, INP, CLS
server response time
route payload and client bundle
request count and waterfall
cache hit/freshness behavior
```

## Forbidden

- Do not optimize from intuition alone.
- Do not cache user-specific or sensitive data incorrectly.
- Do not trade correctness for a benchmark.
- Do not add performance dependencies without approval.
