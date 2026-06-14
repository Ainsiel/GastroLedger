# Architecture Drivers

## Priority Drivers

1. Tenant isolation must hold even when application filtering fails.
2. Inventory changes must remain attributable, balanced and reproducible.
3. Recipe explosion and unit conversion must be deterministic and cycle-free.
4. Cost history must not be rewritten by later purchase or yield changes.
5. Imports and background work must be idempotent.
6. V1 must operate without external APIs and avoid unnecessary infrastructure.
7. Frontend workflows must expose incomplete, stale and exception states honestly.

## Quality Scenarios

| Driver | Stimulus | Expected response |
|---|---|---|
| Isolation | User probes an identifier from another tenant | No data is returned; denial is audited |
| Inventory concurrency | Two commands attempt to consume the same last lot quantity | At most one commits; balance never becomes negative |
| Import retry | Operator retries a timed-out CSV import | Same idempotency key produces no duplicate sale/movement |
| Cost change | Receipt changes ingredient average cost | Affected recipe snapshots update within 5 minutes |
| Worker failure | Cost or alert job fails midway | Business transaction remains valid; job is retryable and visible |
| Recovery | Primary database is lost | Restore meets RPO 15m / RTO 4h and passes smoke checks |

## Main Risks

| Risk | Mitigation |
|---|---|
| Tenant context omitted | RLS, repository guards, integration tests and audit |
| Conversion error amplifies consumption | Versioned conversions, decimal constraints and approval |
| Hot lot contention | Short transactions, deterministic lock order and allocation tests |
| Cost recalculation cascade | Impact graph, coalesced jobs and snapshots |
| Incomplete sales data appears authoritative | Confidence/incomplete states in reports |
| Scope drifts into financial ERP | Explicit no-transaction ADR and vocabulary rules |
