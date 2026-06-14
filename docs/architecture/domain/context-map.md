# Context Map

| Upstream | Downstream | Contract | Coupling rule |
|---|---|---|---|
| Platform & Organization | All contexts | Tenant, actor, branch and warehouse identities | Downstream stores opaque IDs, never writes platform tables |
| Menu Engineering | Inventory & Production | Approved recipe version and unit conversion contract | Inventory never reads mutable draft recipes |
| Menu Engineering | Store Operations | Active menu item/recipe reference | Sales imports require approved version |
| Procurement | Inventory & Production | `SupplierReceiptAccepted`, `SupplierReturnAccepted` | Inventory posts idempotent ledger transactions |
| Inventory & Production | Menu Engineering | Accepted average-cost change | Menu recalculates snapshots asynchronously |
| Store Operations | Inventory & Production | `SaleImportAccepted` lines | Inventory allocates or creates exceptions |
| Store Operations | Control & Insights | Closed sales, cash and attendance facts | Insights consumes immutable facts |
| Inventory & Production | Control & Insights | Movement and count facts | Insights never edits inventory |
| Control & Insights | Procurement / Inventory | Ordering hold decision | Commands query policy before approval |

Cross-context communication occurs through application contracts and outbox events.
No context writes another context's mutable tables.
