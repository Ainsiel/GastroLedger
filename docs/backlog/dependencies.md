# Backlog Dependencies

```text
status = proposed
cycle_check = no cycles detected
```

## Dependency Graph

```text
Foundation
  -> GL-001 Tenant registration and isolation tracer
     -> GL-002 Users, invitations and roles
     -> GL-003 Tenant settings, branches and warehouses
        -> GL-004 Units and ingredients
           -> GL-005 Suppliers and offers
           -> GL-006 Versioned sub-recipes
              -> GL-007 Menu items and margin
                 -> GL-008 Cost snapshot recalculation
        -> GL-016 Ordering holds
        -> GL-019 Cash shifts
        -> GL-020 Workforce operations

GL-003 + GL-004 + GL-005
  -> GL-009 Supplier receipt to inventory ledger
     -> GL-010 Production batch
     -> GL-011 Transfer lifecycle
     -> GL-012 Operational waste
     -> GL-014 Blind physical count
     -> GL-018 Supplier return

GL-008 + GL-009
  -> GL-013 Expiry alerts

GL-007 + GL-008 + GL-009
  -> GL-015 Sales import and allocation exceptions
     -> GL-021 Royalty estimates

GL-005 + GL-016
  -> GL-017 Purchase orders

GL-008 + GL-009 + GL-014 + GL-015 + GL-021
  -> GL-022 Cost variance and menu profitability
     -> GL-023 Tenant data export
```

## Cross-Context Contracts

| Producer | Consumer | First slice that proves contract |
|---|---|---|
| Platform & Organization identities | All contexts | GL-004 |
| Menu approved recipe version | Inventory & Production | GL-010 |
| Menu active menu item reference | Store Operations | GL-015 |
| Procurement receipt accepted | Inventory & Production | GL-009 |
| Inventory ingredient cost changed | Menu Engineering | GL-008/GL-009 |
| Store sale import accepted | Inventory & Production | GL-015 |
| Store and inventory facts | Control & Insights | GL-021/GL-022 |
| Control ordering hold decision | Procurement | GL-017 |

## Sequencing Rules

- Do not begin a blocked issue until all listed dependencies are accepted in
  `develop`.
- Preserve one primary bounded context per work order; consume other contexts only
  through public contracts.
- Shared infrastructure discovered during a slice belongs in that slice only when
  it has a confirmed consumer and acceptance evidence.
- Never create a separate layer-only issue for router, database or UI work.
