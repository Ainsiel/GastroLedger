# System Test Cases

Each test targets one documented use-case flow through observable system behavior.

| Test | Flow | Given / When / Then |
|---|---|---|
| TC-001-S | UC-001-S | Given unique company/admin data, when registration completes, then tenant, admin and scoped session exist. |
| TC-001-A | UC-001-A | Given optional branch data, when onboarding completes, then the first branch belongs only to the new tenant. |
| TC-001-F | UC-001-F | Given duplicate company key, when registering, then no partial tenant or user remains. |
| TC-002-S | UC-002-S | Given tenant admin permission, when valid settings change, then new settings and audit event are visible. |
| TC-002-A | UC-002-A | Given existing branches above a reduced limit, when saving, then branches remain and new creation is blocked. |
| TC-002-F | UC-002-F | Given unsupported currency or forbidden actor, when updating, then settings remain unchanged. |
| TC-003-S | UC-003-S | Given a local user and branch scope, when roles are assigned, then allowed access succeeds and other branches remain hidden. |
| TC-003-A | UC-003-A | Given admin permission, when generating an invitation, then one time-limited local link is usable once. |
| TC-003-F | UC-003-F | Given expired invitation or privilege escalation, when submitted, then access is denied and audited. |
| TC-004-S | UC-004-S | Given remaining tenant capacity, when branch warehouses are created, then each has unique scoped codes. |
| TC-004-A | UC-004-A | Given warehouse with no open movements, when deactivated, then new movements are blocked and history remains. |
| TC-004-F | UC-004-F | Given exceeded limit or duplicate code, when creating, then no branch/warehouse is added. |
| TC-005-S | UC-005-S | Given compatible units, when a positive conversion is saved, then equivalent quantities calculate precisely. |
| TC-005-A | UC-005-A | Given future factor version, when current calculations run, then current factor remains until effective date. |
| TC-005-F | UC-005-F | Given incompatible dimensions or non-positive factor, when saving, then validation explains rejection. |
| TC-006-S | UC-006-S | Given valid units and thresholds, when ingredient is created, then it is available for offers and recipes. |
| TC-006-A | UC-006-A | Given historical usage, when ingredient is archived, then history remains and new recipes cannot use it. |
| TC-006-F | UC-006-F | Given duplicate code or invalid mapping, when saving, then no ingredient is created. |
| TC-007-S | UC-007-S | Given supplier and ingredient, when a valid offer is recorded, then price history and active offer are visible. |
| TC-007-A | UC-007-A | Given future offer, when recorded, then current offer remains active until the future date. |
| TC-007-F | UC-007-F | Given overlap or cross-tenant supplier, when saving, then offer is rejected. |
| TC-008-S | UC-008-S | Given ingredients and yield, when sub-recipe is approved, then version and theoretical cost snapshot exist. |
| TC-008-A | UC-008-A | Given active version, when future version is scheduled, then current production still uses active version. |
| TC-008-F | UC-008-F | Given cycle, invalid yield or excessive depth, when approving, then version is rejected. |
| TC-009-S | UC-009-S | Given costed components, when menu recipe is approved, then cost, margin and suggested price calculate. |
| TC-009-A | UC-009-A | Given branch price override, when saved, then branch margin changes without recipe mutation. |
| TC-009-F | UC-009-F | Given missing component cost, when approving, then approval fails with missing-cost details. |
| TC-010-S | UC-010-S | Given accepted cost change, when worker completes, then all affected active recipe snapshots update. |
| TC-010-A | UC-010-A | Given repeated cost events, when worker leases jobs, then one idempotent result is published. |
| TC-010-F | UC-010-F | Given calculation failure, when job runs, then prior snapshot remains and retry evidence exists. |
| TC-011-S | UC-011-S | Given sufficient FEFO inputs, when batch posts, then inputs decrease and prepared lot increases atomically. |
| TC-011-A | UC-011-A | Given lower actual yield, when batch posts with reason, then yield variance is recorded. |
| TC-011-F | UC-011-F | Given insufficient stock or inactive recipe, when posting, then no movements or prepared lot exist. |
| TC-012-S | UC-012-S | Given selected valid offers, when authorized approval occurs, then purchase order is created. |
| TC-012-A | UC-012-A | Given suggestions, when user edits quantities, then approved order reflects reviewed quantities only. |
| TC-012-F | UC-012-F | Given ordering hold, invalid quantity or forbidden approver, when ordering, then creation fails. |
| TC-013-S | UC-013-S | Given open order and acceptable delivery, when received, then lots, costs and movements commit. |
| TC-013-A | UC-013-A | Given partial delivery, when received, then accepted quantity posts and remainder stays open. |
| TC-013-F | UC-013-F | Given rejected temperature, duplicate lot or excess, when receiving, then affected lines do not post. |
| TC-014-S | UC-014-S | Given available received lot, when return posts, then stock decreases and expected adjustment is recorded. |
| TC-014-A | UC-014-A | Given partially defective lot, when returning subset, then remaining lot balance stays available. |
| TC-014-F | UC-014-F | Given excessive return or closed supplier, when posting, then no movement occurs. |
| TC-015-S | UC-015-S | Given valid warehouses/items, when transfer is approved, then approved request is visible to source. |
| TC-015-A | UC-015-A | Given excessive request, when approver reduces quantities, then approved lines preserve requested history. |
| TC-015-F | UC-015-F | Given same warehouse, hold or invalid item, when requesting, then transfer is rejected. |
| TC-016-S | UC-016-S | Given approved request and stock, when dispatched, then source lots decrease and in-transit quantities appear. |
| TC-016-A | UC-016-A | Given partial availability, when partial dispatch is accepted, then remainder stays pending. |
| TC-016-F | UC-016-F | Given insufficient stock or unapproved request, when dispatching, then no movement occurs. |
| TC-017-S | UC-017-S | Given dispatched transfer, when destination receives, then destination lots preserve source lineage. |
| TC-017-A | UC-017-A | Given transport loss, when receiving with reason, then received and loss movements reconcile dispatched total. |
| TC-017-F | UC-017-F | Given duplicate or excessive receipt, when receiving, then destination balance remains unchanged. |
| TC-018-S | UC-018-S | Given available lot and valid reason, when waste posts, then balance decreases and audit evidence exists. |
| TC-018-A | UC-018-A | Given high-value waste, when submitted, then no movement occurs until separate approval. |
| TC-018-F | UC-018-F | Given missing reason, forbidden actor or excessive quantity, when posting, then no movement occurs. |
| TC-019-S | UC-019-S | Given nearing-expiry lots, when alert job runs, then active in-app alerts are created. |
| TC-019-A | UC-019-A | Given active alert, when acknowledged with note, then action and actor are retained. |
| TC-019-F | UC-019-F | Given repeated job run, when processed, then no duplicate active alerts exist. |
| TC-020-S | UC-020-S | Given blind submitted counts, when manager approves, then variance movements reconcile inventory. |
| TC-020-A | UC-020-A | Given variance above threshold, when reviewed, then recount is required before adjustment. |
| TC-020-F | UC-020-F | Given counter attempts theoretical view or self-approval, when requested, then action is denied. |
| TC-021-S | UC-021-S | Given valid sale lines and stock, when import completes, then recipe explosion consumes FEFO lots once. |
| TC-021-A | UC-021-A | Given mixed valid/shortage lines, when import completes, then valid lines commit and shortage exceptions exist. |
| TC-021-F | UC-021-F | Given duplicate key, unknown item or invalid period, when importing, then affected input is rejected without duplicates. |
| TC-022-S | UC-022-S | Given open shift and closing denominations, when closed, then operational cash variance calculates. |
| TC-022-A | UC-022-A | Given variance over threshold, when manager explains, then reason and review are audited. |
| TC-022-F | UC-022-F | Given duplicate open shift or wrong cashier, when closing, then operation is rejected. |
| TC-023-S | UC-023-S | Given non-overlapping schedule and attendance, when period closes, then worked hours and absences calculate. |
| TC-023-A | UC-023-A | Given overtime candidate, when manager approves exception, then report marks approval without payroll. |
| TC-023-F | UC-023-F | Given overlap or forbidden correction, when saving, then schedule/attendance remains unchanged. |
| TC-024-S | UC-024-S | Given royalty policy and recorded sales, when period calculates, then non-financial estimate is reproducible. |
| TC-024-A | UC-024-A | Given controller reason, when hold changes, then purchase eligibility and audit update. |
| TC-024-F | UC-024-F | Given missing policy or forbidden actor, when calculating/changing hold, then action is rejected. |
| TC-025-S | UC-025-S | Given closed period and snapshots, when report runs, then theoretical, actual and profitability metrics reconcile. |
| TC-025-A | UC-025-A | Given filters, when applied, then results and totals remain consistent for selected scope. |
| TC-025-F | UC-025-F | Given incomplete inputs, when report runs, then incomplete status and reasons appear instead of final figures. |

## Test Boundaries

- System tests exercise Next.js-visible outcomes through approved FastAPI contracts.
- Integration tests separately prove PostgreSQL constraints, RLS, transactions,
  jobs, FEFO allocation and idempotency.
- No test requires Internet, external APIs, payment providers or real personal data.
