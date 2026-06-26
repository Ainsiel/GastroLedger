# Aggregate Design

| Aggregate | Invariant and transaction boundary |
|---|---|
| Tenant | Registration creates tenant, settings and first admin membership atomically |
| Recipe Version | Approved version is cycle-free, dimension-valid and immutable |
| Purchase Order | Approved quantity and supplier offer reference remain traceable |
| Supplier Receipt | Accepted receipt lines create lots and one inventory transaction atomically |
| Inventory Transaction | Entries are immutable, tenant/warehouse scoped and cannot create negative available lot balance |
| Production Batch | Input consumption and prepared output lot commit together |
| Transfer | Dispatch cannot exceed approved quantity; total receipt/loss cannot exceed dispatch |
| Physical Count | Only reviewed count can produce one variance transaction |
| Sales Import | Idempotency key is unique; lines become accepted, exception or rejected |
| Cash Shift | One open shift per cashier/branch; closing records become immutable after review |
| Ordering Hold | Active hold requires controller, reason and effective period |

Aggregates reference other aggregates by identity. Cost/report projections are not
placed inside transactional aggregates.
