# Data Model Design

```text
database = PostgreSQL
logical_relations = 54
tenant_model = shared schema with tenant_id and RLS
```

## Platform And Organization (11)

| Relation | Purpose | Key constraints |
|---|---|---|
| `platform_tenants` | Tenant identity and lifecycle | Unique immutable slug |
| `platform_tenant_settings` | Locale, base currency and operational limits | One per tenant |
| `platform_users` | Local credential identity | Unique normalized login |
| `platform_memberships` | User membership in tenant | Unique tenant/user |
| `platform_roles` | Tenant-defined scoped roles | Unique tenant/name |
| `platform_role_grants` | Capabilities granted to role | Unique role/capability/scope type |
| `platform_membership_roles` | Role assignments and optional branch scope | Valid membership/role same tenant |
| `platform_sessions` | Revocable local sessions | Hashed token, expiry |
| `platform_invitations` | Time-limited manual invitation links | Hashed token, single use |
| `platform_branches` | Restaurant locations | Unique tenant/code |
| `platform_warehouses` | Stock locations | Unique branch/code |

## Menu Engineering (10)

| Relation | Purpose | Key constraints |
|---|---|---|
| `menu_units` | Units and dimensions | Unique tenant/code |
| `menu_conversion_factors` | Effective-dated compatible conversions | Positive factor, no overlap |
| `menu_ingredients` | Ingredient master | Unique tenant/code |
| `menu_ingredient_branch_policies` | Critical stock and branch costing policy | Unique branch/ingredient |
| `menu_recipes` | Stable recipe identity and type | Type is sub-recipe or menu item |
| `menu_recipe_versions` | Immutable approved/draft versions | Unique recipe/version |
| `menu_recipe_components` | Versioned ingredient/sub-recipe quantities | One component type, positive quantity |
| `menu_item_branch_prices` | Informational selling price by branch | Effective-dated, no overlap |
| `menu_cost_snapshots` | Reproducible recipe cost result/status | Unique recipe version/branch/as-of |
| `menu_cost_snapshot_lines` | Component contribution to cost | Sum explains snapshot total |

## Procurement (8)

| Relation | Purpose | Key constraints |
|---|---|---|
| `procurement_suppliers` | Supplier master | Unique tenant/code |
| `procurement_supplier_offers` | Effective ingredient offer and price history | Supplier/ingredient/unit/effective date |
| `procurement_purchase_orders` | Order lifecycle | Unique tenant/order number |
| `procurement_purchase_order_lines` | Ordered offer quantities | Positive quantity |
| `procurement_supplier_receipts` | Receipt lifecycle and temperature evidence | Unique tenant/receipt number |
| `procurement_supplier_receipt_lines` | Accepted/rejected lot details | Quantity and tolerance constraints |
| `procurement_supplier_returns` | Operational supplier return | References accepted receipt |
| `procurement_supplier_return_lines` | Returned lot quantity and expected adjustment | Cannot exceed available lot balance |

## Inventory And Production (12)

| Relation | Purpose | Key constraints |
|---|---|---|
| `inventory_lots` | Traceable stock lot and lineage | Unique tenant/warehouse/lot code |
| `inventory_transactions` | Atomic immutable stock reason | Tenant, type, source and posted time |
| `inventory_entries` | Signed lot quantity/cost movement | Immutable; references transaction and lot |
| `inventory_stock_balances` | Current quantity projection | Unique lot; cannot be negative |
| `inventory_production_batches` | Production lifecycle, recipe version and yield | Unique tenant/batch number |
| `inventory_transfers` | Request/approval/dispatch/receipt lifecycle | Source differs from destination |
| `inventory_transfer_lines` | Requested, approved, dispatched and received totals | Monotonic quantity constraints |
| `inventory_waste_records` | Waste reason and approval state | Posted record references transaction |
| `inventory_expiry_alerts` | Active/acknowledged expiry warning | One active alert per lot/rule |
| `inventory_physical_counts` | Blind count lifecycle | Counter cannot approve own count |
| `inventory_physical_count_lines` | Blind counted quantities and variance | Unique count/lot or item scope |
| `inventory_allocation_exceptions` | Unallocated demand requiring action | Unique source line/reason while open |

## Store Operations (6)

| Relation | Purpose | Key constraints |
|---|---|---|
| `store_sales_imports` | Import/simulation job and idempotency | Unique tenant/branch/idempotency key |
| `store_sales_records` | Operational sale grouping | Unique import/source reference |
| `store_sales_lines` | Menu item quantity and allocation status | Positive quantity |
| `store_cash_shifts` | Opening/closing operational reconciliation | One open cashier/branch shift |
| `store_work_shifts` | Planned employee branch shift | No overlapping confirmed assignment |
| `store_attendance_records` | Actual attendance and corrections | Audited correction lifecycle |

## Control And Insights (7)

| Relation | Purpose | Key constraints |
|---|---|---|
| `control_royalty_policies` | Effective non-financial percentage/rule | No overlapping active policy |
| `control_royalty_estimates` | Reproducible period estimate | Unique branch/policy/period |
| `control_ordering_holds` | Manual governed hold | Actor, reason and effective range required |
| `control_audit_events` | Append-only protected action evidence | Actor/correlation/object required |
| `control_jobs` | Durable leased background work | Idempotency, attempts and lease constraints |
| `control_outbox_events` | Committed cross-context facts | Event ID unique, publish state |
| `control_notifications` | In-app user/role alert | Tenant-scoped recipient and state |

## Cross-Cutting Constraints

- Every tenant-owned relation includes non-null `tenant_id` and RLS.
- Cross-context references use opaque identifiers and application validation; foreign
  keys are used inside one context.
- Quantity, cost and conversion values use bounded numeric precision, never float.
- Inventory entries and audit events are append-only.
- Approved recipe versions and historical snapshots are immutable.
- Time ranges use exclusion/uniqueness constraints where overlap is forbidden.

## Index Rationale

- Tenant key leads all tenant-scoped indexes.
- FEFO lookup indexes warehouse, ingredient/prepared item, available status, expiry
  and received time.
- Job leasing indexes ready state and availability time.
- Imports and commands have unique idempotency indexes.
- Reporting indexes are added only for confirmed period/branch queries.

## Migration Strategy

Use expand/migrate/contract changes. RLS policies, constraints and migrations are
verified against a real PostgreSQL test environment. Destructive cleanup occurs
only after compatible application versions and rollback window expire.
