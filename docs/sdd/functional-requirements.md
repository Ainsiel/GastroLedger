# Functional Requirements

## Platform And Organization

| ID | Requirement |
|---|---|
| FR-001 | The system must register a company tenant and its first administrator without payment. |
| FR-002 | The system must manage tenant settings, operational limits and base currency without currency conversion. |
| FR-003 | The system must manage local users, invitations, roles and scoped permissions. |
| FR-004 | The system must manage branches and their internal warehouses. |

## Menu Engineering

| ID | Requirement |
|---|---|
| FR-005 | The system must manage units and validated conversion factors. |
| FR-006 | The system must manage ingredients, purchase/consumption units and reorder thresholds. |
| FR-007 | The system must define sub-recipes with ingredients, yield and maximum nesting depth. |
| FR-008 | The system must define menu item recipes using ingredients or sub-recipes. |
| FR-009 | The system must calculate theoretical cost, contribution margin and suggested price. |
| FR-010 | The system must recalculate affected costs after accepted cost or yield changes. |

## Procurement

| ID | Requirement |
|---|---|
| FR-011 | The system must manage suppliers, product offers and price history. |
| FR-012 | The system must produce reorder suggestions and allow approved purchase orders. |
| FR-013 | The system must receive purchase orders with lots, quantities, cost, expiry and temperature. |
| FR-014 | The system must record supplier returns and expected non-financial adjustments. |

## Inventory And Production

| ID | Requirement |
|---|---|
| FR-015 | The system must create production batches that consume inputs and create prepared lots. |
| FR-016 | The system must request, approve, dispatch and receive stock transfers. |
| FR-017 | The system must record operational waste with reason and evidence. |
| FR-018 | The system must allocate expiring lots by FEFO and create in-app alerts. |
| FR-019 | The system must perform blind counts and reconcile approved variances. |
| FR-020 | The system must prevent unexplained or negative stock movements. |

## Store Operations And Control

| ID | Requirement |
|---|---|
| FR-021 | The system must import or simulate sales and explode approved recipes into inventory consumption. |
| FR-022 | The system must create actionable exceptions when sales cannot be allocated. |
| FR-023 | The system must record cash shift opening and closing reconciliation without processing payments. |
| FR-024 | The system must plan shifts and record attendance without calculating payroll. |
| FR-025 | The system must calculate non-financial royalty estimates and manage manual ordering holds. |
| FR-026 | The system must report cost variance and menu profitability by branch and period. |

## Cross-Cutting

| ID | Requirement |
|---|---|
| FR-027 | The system must record an attributable audit trail for protected actions. |
| FR-028 | The system must expose only tenant-scoped data to authenticated users. |
| FR-029 | The system must deliver alerts only through the application interface. |
| FR-030 | The system must support bounded CSV imports with preview, validation and idempotency. |
| FR-031 | The system must preserve historical recipe, cost and movement snapshots. |
| FR-032 | The system must provide open-format tenant exports without transmitting data externally. |
