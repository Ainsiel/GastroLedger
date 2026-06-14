# Integration Test Cases

| ID | Boundary | Scenario | Expected evidence |
|---|---|---|---|
| IT-001 | Registration + PostgreSQL | Two concurrent registrations use same tenant slug | One tenant/admin commits |
| IT-002 | API + RLS | User requests another tenant's known identifier | No data; denial/audit evidence |
| IT-003 | Worker + RLS | Job tenant context differs from referenced object | Job fails safely without data access |
| IT-004 | Roles + API | Branch-scoped role probes another branch | Forbidden/hidden result |
| IT-005 | Units + recipes | Incompatible unit reaches recipe approval | Transaction rejects approval |
| IT-006 | Recipes + PostgreSQL | Concurrent approval of same draft version | One immutable version wins |
| IT-007 | Recipe graph | Sub-recipe cycle/depth violation | Stable validation problem |
| IT-008 | Receipt + inventory | Accepted receipt posts lots and ledger | Receipt and entries commit atomically |
| IT-009 | Receipt idempotency | Same receipt acceptance retries | No duplicate lots or entries |
| IT-010 | Inventory concurrency | Two consumers allocate last quantity | One succeeds; no negative balance |
| IT-011 | Production | Input shortage during posting | No input/output entry commits |
| IT-012 | Transfer | Dispatch and cancellation race | One valid state transition commits |
| IT-013 | Transfer | Duplicate destination receipt | No duplicate stock |
| IT-014 | Waste approval | High-value waste posts before approval | Posting is blocked |
| IT-015 | Physical count | Counter attempts own approval | Denied and audited |
| IT-016 | Sales import | Repeated idempotency key | One import and one consumption result |
| IT-017 | Sales import | Mixed valid and shortage lines | Valid commits; explicit exceptions |
| IT-018 | Cost jobs | Repeated ingredient cost events | One latest reproducible snapshot |
| IT-019 | Job queue | Worker dies after lease | Lease expires and safe retry succeeds |
| IT-020 | Outbox | Consumer fails after source commit | Source stays committed; event retries |
| IT-021 | Ordering hold | Purchase approval during active hold | Approval denied with hold reason |
| IT-022 | Cash shift | Two openings for cashier/branch | Unique open-shift rule holds |
| IT-023 | Work shifts | Overlapping confirmed assignment | Database/application conflict |
| IT-024 | Report | Open import exists in period | Report marked incomplete |
| IT-025 | Tenant export | Authorized export requested | Only tenant data and ledger included |
