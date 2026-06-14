# GitHub Issue Publication Plan

```text
status = draft
approved = false
repo = Ainsiel/GastroLedger
remote_writes_performed = false
batch_size = 5
```

## Read-Only Audit

- Existing GitHub issues: `0`.
- Existing approved Gridwork labels: `0`.
- GitHub currently contains only default repository labels.

## Approved Labels Needed

Only labels from `.gridwork/policies/github-labels.json` are proposed:

| Label | Use |
|---|---|
| `gridwork` | All drafts |
| `type:feature` | All product slices |
| `slice:vertical` | All drafts |
| `status:ready` | GL-001 only |
| `mode:afk` | TDD work-order candidates |
| `agent:implementer` | Intended implementation owner |
| `workflow:tdd-implementation` | Intended delivery workflow |

Creating labels is a separate GitHub write gate.

## Proposed Label Commands

```powershell
gh label create gridwork --repo Ainsiel/GastroLedger --color 5319e7 --description "Gridwork factory work."
gh label create "type:feature" --repo Ainsiel/GastroLedger --color 0e8a16 --description "Feature or enabling capability."
gh label create "slice:vertical" --repo Ainsiel/GastroLedger --color 1d76db --description "End-to-end vertical slice."
gh label create "status:ready" --repo Ainsiel/GastroLedger --color 0e8a16 --description "Ready for execution."
gh label create "mode:afk" --repo Ainsiel/GastroLedger --color d4c5f9 --description "AFK delegated work."
gh label create "agent:implementer" --repo Ainsiel/GastroLedger --color f9d0c4 --description "Implementer agent."
gh label create "workflow:tdd-implementation" --repo Ainsiel/GastroLedger --color fef2c0 --description "TDD implementation workflow."
```

## Proposed Issue Commands

These commands are exact proposals and have not been executed:

```powershell
gh issue create --repo Ainsiel/GastroLedger --title "Register a tenant and prove isolation" --body-file "docs/backlog/issues/GL-001-tenant-registration-isolation.md" --label "gridwork,type:feature,slice:vertical,status:ready,mode:afk,agent:implementer,workflow:tdd-implementation"
gh issue create --repo Ainsiel/GastroLedger --title "Manage local users, invitations and scoped roles" --body-file "docs/backlog/issues/GL-002-local-users-scoped-roles.md" --label "gridwork,type:feature,slice:vertical,mode:afk,agent:implementer,workflow:tdd-implementation"
gh issue create --repo Ainsiel/GastroLedger --title "Configure tenant settings, branches and warehouses" --body-file "docs/backlog/issues/GL-003-tenant-operating-scope.md" --label "gridwork,type:feature,slice:vertical,mode:afk,agent:implementer,workflow:tdd-implementation"
gh issue create --repo Ainsiel/GastroLedger --title "Manage units and ingredient catalog" --body-file "docs/backlog/issues/GL-004-units-ingredient-catalog.md" --label "gridwork,type:feature,slice:vertical,mode:afk,agent:implementer,workflow:tdd-implementation"
gh issue create --repo Ainsiel/GastroLedger --title "Manage suppliers and effective-dated offers" --body-file "docs/backlog/issues/GL-005-suppliers-effective-offers.md" --label "gridwork,type:feature,slice:vertical,mode:afk,agent:implementer,workflow:tdd-implementation"
gh issue create --repo Ainsiel/GastroLedger --title "Approve versioned sub-recipes" --body-file "docs/backlog/issues/GL-006-versioned-sub-recipes.md" --label "gridwork,type:feature,slice:vertical,mode:afk,agent:implementer,workflow:tdd-implementation"
gh issue create --repo Ainsiel/GastroLedger --title "Approve menu items and branch margin" --body-file "docs/backlog/issues/GL-007-menu-items-margin.md" --label "gridwork,type:feature,slice:vertical,mode:afk,agent:implementer,workflow:tdd-implementation"
gh issue create --repo Ainsiel/GastroLedger --title "Recalculate recipe cost snapshots asynchronously" --body-file "docs/backlog/issues/GL-008-cost-snapshot-recalculation.md" --label "gridwork,type:feature,slice:vertical,mode:afk,agent:implementer,workflow:tdd-implementation"
gh issue create --repo Ainsiel/GastroLedger --title "Receive a supplier delivery into the inventory ledger" --body-file "docs/backlog/issues/GL-009-supplier-receipt-inventory-ledger.md" --label "gridwork,type:feature,slice:vertical,mode:afk,agent:implementer,workflow:tdd-implementation"
gh issue create --repo Ainsiel/GastroLedger --title "Post a production batch and prepared lot" --body-file "docs/backlog/issues/GL-010-production-batch.md" --label "gridwork,type:feature,slice:vertical,mode:afk,agent:implementer,workflow:tdd-implementation"
gh issue create --repo Ainsiel/GastroLedger --title "Complete a stock transfer lifecycle" --body-file "docs/backlog/issues/GL-011-stock-transfer-lifecycle.md" --label "gridwork,type:feature,slice:vertical,mode:afk,agent:implementer,workflow:tdd-implementation"
gh issue create --repo Ainsiel/GastroLedger --title "Record operational waste with approval evidence" --body-file "docs/backlog/issues/GL-012-operational-waste.md" --label "gridwork,type:feature,slice:vertical,mode:afk,agent:implementer,workflow:tdd-implementation"
gh issue create --repo Ainsiel/GastroLedger --title "Create and acknowledge expiry alerts" --body-file "docs/backlog/issues/GL-013-expiry-alerts.md" --label "gridwork,type:feature,slice:vertical,mode:afk,agent:implementer,workflow:tdd-implementation"
gh issue create --repo Ainsiel/GastroLedger --title "Perform a blind count and reconcile variance" --body-file "docs/backlog/issues/GL-014-blind-physical-count.md" --label "gridwork,type:feature,slice:vertical,mode:afk,agent:implementer,workflow:tdd-implementation"
gh issue create --repo Ainsiel/GastroLedger --title "Import sales and resolve allocation exceptions" --body-file "docs/backlog/issues/GL-015-sales-import-allocation-exceptions.md" --label "gridwork,type:feature,slice:vertical,mode:afk,agent:implementer,workflow:tdd-implementation"
gh issue create --repo Ainsiel/GastroLedger --title "Apply manual ordering holds" --body-file "docs/backlog/issues/GL-016-ordering-holds.md" --label "gridwork,type:feature,slice:vertical,mode:afk,agent:implementer,workflow:tdd-implementation"
gh issue create --repo Ainsiel/GastroLedger --title "Create approved purchase orders" --body-file "docs/backlog/issues/GL-017-approved-purchase-orders.md" --label "gridwork,type:feature,slice:vertical,mode:afk,agent:implementer,workflow:tdd-implementation"
gh issue create --repo Ainsiel/GastroLedger --title "Record supplier return and expected adjustment" --body-file "docs/backlog/issues/GL-018-supplier-return.md" --label "gridwork,type:feature,slice:vertical,mode:afk,agent:implementer,workflow:tdd-implementation"
gh issue create --repo Ainsiel/GastroLedger --title "Reconcile an operational cash shift" --body-file "docs/backlog/issues/GL-019-operational-cash-shift.md" --label "gridwork,type:feature,slice:vertical,mode:afk,agent:implementer,workflow:tdd-implementation"
gh issue create --repo Ainsiel/GastroLedger --title "Plan shifts and record attendance" --body-file "docs/backlog/issues/GL-020-workforce-operations.md" --label "gridwork,type:feature,slice:vertical,mode:afk,agent:implementer,workflow:tdd-implementation"
gh issue create --repo Ainsiel/GastroLedger --title "Calculate non-financial royalty estimates" --body-file "docs/backlog/issues/GL-021-royalty-estimates.md" --label "gridwork,type:feature,slice:vertical,mode:afk,agent:implementer,workflow:tdd-implementation"
gh issue create --repo Ainsiel/GastroLedger --title "Analyze cost variance and menu profitability" --body-file "docs/backlog/issues/GL-022-cost-variance-menu-profitability.md" --label "gridwork,type:feature,slice:vertical,mode:afk,agent:implementer,workflow:tdd-implementation"
gh issue create --repo Ainsiel/GastroLedger --title "Export tenant data in open formats" --body-file "docs/backlog/issues/GL-023-tenant-data-export.md" --label "gridwork,type:feature,slice:vertical,mode:afk,agent:implementer,workflow:tdd-implementation"
```

Add `status:ready` only to `GL-001`. Publish in dependency order, five issues per
approved batch. After each batch, record returned URLs, verify labels and confirm
that body traceability survived publication before continuing.

## Publication Gates

1. Approve creation of the seven missing labels.
2. Approve the exact issue batch and titles.
3. Execute `gh issue create` commands.
4. Read back published issues and reconcile URLs into the local snapshot.

No command in this plan has been executed.
