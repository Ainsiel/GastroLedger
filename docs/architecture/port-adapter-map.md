# Port And Adapter Map

| Port | Consumer | Reason | Known adapter | Failure contract | Test strategy |
|---|---|---|---|---|---|
| `TenantContext` | All application contexts | Mandatory isolation boundary | Session + PostgreSQL transaction context | Missing context denies operation | Cross-tenant integration tests |
| `AuthorizationPolicy` | Commands/queries | Central scoped access decision | Platform role grants | Stable forbidden result | Policy unit + API integration |
| `RecipeCatalog` | Inventory, Store Operations | Use immutable approved recipe versions | Menu application adapter | Missing/inactive version | Contract tests |
| `UnitConversionPolicy` | Menu, Inventory | Deterministic decimal conversion | Menu domain service | Incompatible units | Domain tests |
| `InventoryLedger` | Procurement, Inventory, Store | Atomic lot entries and no-negative invariant | PostgreSQL ledger adapter | Conflict/insufficient stock | Transaction/concurrency tests |
| `LotAllocator` | Production, transfer, sales | FEFO/FIFO policy isolation | Domain policy implementation | Allocation exception detail | Domain + PostgreSQL tests |
| `CostProjection` | Menu, Insights | Snapshot recalculation boundary | PostgreSQL projection adapter | Stale/failed status retained | Worker integration tests |
| `JobQueue` | API and worker | Durable local async work | PostgreSQL lease queue | Retry/exhausted visible | Lease/concurrency tests |
| `EventOutbox` | State-changing use cases | Reliable cross-context facts | PostgreSQL outbox | Append failure blocks source commit | Atomicity tests |
| `AuditSink` | Protected use cases | Attributable evidence | PostgreSQL audit adapter | Critical audit failure blocks command | Atomicity tests |
| `Clock` | All contexts | Deterministic effective dates | System clock / fixed test clock | N/A | Unit tests |
| `ImportReader` | Store Operations | Bounded CSV parsing without external storage | Streaming CSV adapter | Row-level validation errors | Import integration tests |

No external network adapter is approved for V1.
