# Ubiquitous Language

| Term | Definition | Context | Avoid |
|---|---|---|---|
| Tenant | Restaurant holding, chain or franchise operator isolated in the SaaS | Platform | customer account, subscription |
| Branch | Operational restaurant location belonging to one tenant | Platform | store when it means warehouse |
| Warehouse | Stock-holding area inside or associated with a branch | Platform / Inventory | branch |
| Unit | Named measure with a dimension such as mass, volume or count | Menu | arbitrary text quantity |
| Conversion factor | Versioned ratio between compatible units | Menu | recipe yield |
| Ingredient | Purchasable and consumable stock item | Menu / Inventory | product |
| Recipe | Versioned composition that yields a sub-recipe or menu item | Menu | BOM table |
| Sub-recipe | Prepared intermediate stock item produced from ingredients | Menu / Inventory | nested item |
| Yield | Actual or expected output quantity of production | Menu / Inventory | conversion factor |
| Lot | Traceable quantity with origin, received/produced date and optional expiry | Inventory | balance |
| Inventory transaction | Atomic reason that creates one or more immutable stock entries | Inventory | editable movement |
| Stock balance | Projection of available quantity from accepted ledger entries | Inventory | source of truth |
| FEFO | Allocation policy choosing the earliest expiry first | Inventory | PEPS when expiry exists |
| Allocation exception | Actionable record explaining why requested consumption could not post | Inventory | negative stock |
| Sale record | Operational statement that menu items were sold; not a payment | Store Operations | transaction, settlement |
| Cash shift | Operational opening/closing count; not payment processing | Store Operations | cash transaction |
| Royalty estimate | Informational calculation from recorded sales and a policy | Control | invoice, charge, liquidation |
| Ordering hold | Manual governance decision that blocks new purchase/transfer requests | Control | automatic debt collection |
| Theoretical cost | Cost calculated from recipe quantities and accepted cost snapshot | Menu | actual consumption |
| Actual cost | Cost represented by posted inventory entries for a period | Inventory / Insights | payment |

## Important Language Rules

- A balance is a projection; the ledger is the stock truth.
- A sale record triggers operational consumption but is not a monetary transaction.
- A royalty estimate never creates a receivable or payment obligation.
- FEFO is used for expiry-sensitive lots; FIFO is the fallback.
