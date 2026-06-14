# ADR-0004: Version Recipes And Preserve Cost Snapshots

```text
status = proposed
```

## Decision

Approved recipe versions are immutable and limited to menu item -> sub-recipe ->
ingredient depth. Theoretical costs are preserved as branch/as-of snapshots using
moving weighted average ingredient costs.

## Consequences

- Production and sales reference the exact approved recipe version.
- Later cost or yield changes never rewrite historical snapshots.
- Cost recalculation is asynchronous, idempotent and explicitly exposes stale/failed
  status.
- Deeper recursion or another valuation policy requires a new decision.
