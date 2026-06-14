# Domain And Integration Events

| Event | Producer | Primary consumers | Delivery |
|---|---|---|---|
| `TenantRegistered` | Platform | Control | Outbox, at least once |
| `RecipeVersionApproved` | Menu | Menu cost worker, Store Operations | Outbox, idempotent |
| `IngredientCostChanged` | Inventory | Menu cost worker | Outbox, coalesced |
| `PurchaseOrderApproved` | Procurement | Notifications | Outbox |
| `SupplierReceiptAccepted` | Procurement | Inventory, Menu cost worker | Same-command contract plus outbox fact |
| `ProductionBatchPosted` | Inventory | Insights | Outbox |
| `TransferDispatched` | Inventory | Notifications | Outbox |
| `TransferReceived` | Inventory | Insights | Outbox |
| `PhysicalCountAdjusted` | Inventory | Insights | Outbox |
| `SaleImportAccepted` | Store Operations | Inventory allocation worker, Insights | Outbox |
| `AllocationExceptionCreated` | Inventory | Notifications, Insights | Outbox |
| `OrderingHoldChanged` | Control | Procurement, Inventory request policy | Policy query plus outbox audit |

Handlers use event identifiers and idempotency records. Eventual consumers must not
change the already committed source transaction.
