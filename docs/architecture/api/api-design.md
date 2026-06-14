# API Design

```text
style = versioned JSON over HTTPS
base_path = /api/v1
consumers = Next.js web, FastAPI worker internal invocation
external_public_api = none
```

## Contract Rules

- Operations are capability-oriented, not generic table CRUD.
- Tenant is resolved from the local session; clients cannot choose arbitrary tenant
  IDs.
- Branch scope is explicit where a capability operates on one branch.
- Decimal quantities and money-like informational values travel as strings.
- Commands accept idempotency keys when retry could duplicate effects.
- Errors use one machine-readable problem shape with correlation ID.
- Collections are bounded, paginated and filterable.

## Representative Operations

| Operation | Success | Main errors | Authorization | Idempotency |
|---|---|---|---|---|
| `POST /tenants/register` | Tenant and first admin session | duplicate, validation | Public bounded registration | Registration key |
| `POST /recipes/{id}/versions/{version}/approve` | Approved immutable version | cycle, missing cost, conflict | Menu engineer | Version conflict |
| `POST /production-batches/{id}/post` | Input/output ledger transaction | insufficient stock, stale recipe | Production lead | Batch ID |
| `POST /purchase-orders/{id}/approve` | Approved order | hold, invalid offer, conflict | Purchasing approver | Order/version |
| `POST /supplier-receipts/{id}/accept` | Lots and ledger transaction | temperature, duplicate lot, tolerance | Warehouse receiver | Receipt ID |
| `POST /transfers/{id}/dispatch` | In-transit entries | insufficient stock, state conflict | Source operator | Dispatch command ID |
| `POST /physical-counts/{id}/approve` | Variance transaction | recount required, self-approval | Branch manager | Count/version |
| `POST /sales-imports` | Accepted import job | duplicate key, invalid file | Branch manager | Required import key |
| `GET /sales-imports/{id}` | Status, errors and exceptions | not found/hidden | Branch scope | N/A |
| `GET /reports/cost-variance` | Complete or explicitly incomplete report | invalid period | Analyst | N/A |

## Problem Shape

```json
{
  "type": "inventory.insufficient_stock",
  "title": "Stock could not be allocated",
  "status": 409,
  "correlationId": "opaque-id",
  "errors": [
    {"field": "lines[2].quantity", "code": "insufficient", "detail": "review allocation exception"}
  ]
}
```

## Compatibility

- Additive changes are preferred within `/api/v1`.
- Breaking contract changes require a new version or compatibility window.
- OpenAPI is generated from public transport schemas and used for consumer contract
  verification.
- Domain and persistence models are never exported as API schemas.
