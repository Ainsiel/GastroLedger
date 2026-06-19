# Backlog Snapshot

```text
run_id = backlog-management-20260614-01
generated_at = 2026-06-19
sources = docs/sdd, docs/architecture, repository structure, GitHub read-only audit
status = published and reconciled after PR #30 creation
github_issues_observed = 23
```

## Summary

| Readiness | Count |
|---|---:|
| Done | 5 |
| In PR | 1 |
| Ready candidate | 4 |
| Defined, blocked by dependencies | 13 |
| Needs requirement refinement | 0 |
| Published | 23 |

The repository contains the bootstrap, architecture foundation, delivery
infrastructure, approved shadcn/ui frontend foundation, local Swagger contract,
SQLAlchemy technical adapters and an isolated PostgreSQL harness. GL-001 through
GL-005 are accepted in `develop`.

## Items

| ID | Outcome | Primary context | Trace | Readiness | Dependencies |
|---|---|---|---|---|---|
| [GL-001](https://github.com/Ainsiel/GastroLedger/issues/1) | Register a tenant and prove isolation | Platform & Organization | UC-001 | Done | Foundation |
| [GL-002](https://github.com/Ainsiel/GastroLedger/issues/2) | Manage local users, invitations and scoped roles | Platform & Organization | UC-003 | Done | GL-001 |
| [GL-003](https://github.com/Ainsiel/GastroLedger/issues/3) | Configure tenant settings, branches and warehouses | Platform & Organization | UC-002, UC-004 | Done | GL-001 |
| [GL-004](https://github.com/Ainsiel/GastroLedger/issues/4) | Manage units and ingredient catalog | Menu Engineering | UC-005, UC-006 | Done | GL-003 |
| [GL-005](https://github.com/Ainsiel/GastroLedger/issues/5) | Manage suppliers and effective-dated offers | Procurement | UC-007 | Done | GL-004 |
| [GL-006](https://github.com/Ainsiel/GastroLedger/issues/6) | Approve versioned sub-recipes | Menu Engineering | UC-008 | In PR | GL-004 |
| [GL-007](https://github.com/Ainsiel/GastroLedger/issues/7) | Approve menu items and branch margin | Menu Engineering | UC-009 | Blocked | GL-006 |
| [GL-008](https://github.com/Ainsiel/GastroLedger/issues/8) | Recalculate recipe cost snapshots asynchronously | Menu Engineering | UC-010 | Blocked | GL-007 |
| [GL-009](https://github.com/Ainsiel/GastroLedger/issues/9) | Receive a supplier delivery into the inventory ledger | Procurement | UC-013 | Ready | GL-005 |
| [GL-010](https://github.com/Ainsiel/GastroLedger/issues/10) | Post a production batch and prepared lot | Inventory & Production | UC-011 | Blocked | GL-006, GL-009 |
| [GL-011](https://github.com/Ainsiel/GastroLedger/issues/11) | Complete a stock transfer lifecycle | Inventory & Production | UC-015 to UC-017 | Blocked | GL-009 |
| [GL-012](https://github.com/Ainsiel/GastroLedger/issues/12) | Record operational waste with approval evidence | Inventory & Production | UC-018 | Blocked | GL-009 |
| [GL-013](https://github.com/Ainsiel/GastroLedger/issues/13) | Create and acknowledge expiry alerts | Inventory & Production | UC-019 | Blocked | GL-008, GL-009 |
| [GL-014](https://github.com/Ainsiel/GastroLedger/issues/14) | Perform a blind count and reconcile variance | Inventory & Production | UC-020 | Blocked | GL-002, GL-009 |
| [GL-015](https://github.com/Ainsiel/GastroLedger/issues/15) | Import sales and resolve allocation exceptions | Store Operations | UC-021 | Blocked | GL-008, GL-009 |
| [GL-016](https://github.com/Ainsiel/GastroLedger/issues/16) | Apply manual ordering holds | Control & Insights | UC-024, flows A/F | Ready | GL-002, GL-003 |
| [GL-017](https://github.com/Ainsiel/GastroLedger/issues/17) | Create approved purchase orders | Procurement | UC-012 | Blocked | GL-009, GL-016 |
| [GL-018](https://github.com/Ainsiel/GastroLedger/issues/18) | Record supplier return and expected adjustment | Procurement | UC-014 | Blocked | GL-009 |
| [GL-019](https://github.com/Ainsiel/GastroLedger/issues/19) | Reconcile an operational cash shift | Store Operations | UC-022 | Ready | GL-002, GL-003 |
| [GL-020](https://github.com/Ainsiel/GastroLedger/issues/20) | Plan shifts and record attendance | Store Operations | UC-023 | Ready | GL-002, GL-003 |
| [GL-021](https://github.com/Ainsiel/GastroLedger/issues/21) | Calculate non-financial royalty estimates | Control & Insights | UC-024, flow S | Blocked | GL-015 |
| [GL-022](https://github.com/Ainsiel/GastroLedger/issues/22) | Analyze cost variance and menu profitability | Control & Insights | UC-025 | Blocked | GL-014, GL-015 |
| [GL-023](https://github.com/Ainsiel/GastroLedger/issues/23) | Export tenant data in open formats | Platform & Organization | FR-032, IT-025 | Blocked | Terminal V1 slices |

## Tracer Slice

`GL-001` delivered the initial tracer and proved the highest-risk path before broader
feature work:

```text
Next.js registration -> FastAPI command -> tenant aggregate -> PostgreSQL transaction
-> RLS tenant context -> local session -> isolated authenticated read
```

It established production migrations for the minimum Platform & Organization
relations, RLS, transaction-scoped tenant context, password/session security,
transport contracts, visible registration states and cross-tenant integration
evidence.

## Missing Work And Gaps

- Exact endpoint paths and DTO field names must be selected inside each approved
  work order while preserving the existing public module boundaries.
- Every frontend-bearing issue now follows
  `docs/backlog/frontend-delivery-contract.md`; missing frontend contract fields make
  an item `needs_refinement`, not ready.
- The approved documents define complete behavior, but performance baselines remain
  deferred until representative data exists.
- `GL-023` is intentionally last because a complete export must cover the accepted
  V1 source facts without external transmission.

## Source Conflicts And Freshness

- The architecture backlog groups work into ten broad slices. These drafts preserve
  its sequence but split large lifecycles into implementable outcomes.
- ADR files have documentary status `proposed`, but the user explicitly supplied
  them as approved workflow sources.
- GitHub publication was explicitly approved on 2026-06-14. On 2026-06-15, issues
  `#1` through `#23` were reconciled with the frontend delivery contract.
- On 2026-06-16, PR #26 delivered GL-003, PR #27 delivered GL-004 and PR #28
  delivered GL-002 into `develop`; issues #2, #3 and #4 are closed as completed
  in GitHub.
- On 2026-06-16, PR #29 delivered GL-005 into `develop`; issue #5 is closed as
  completed in GitHub and GL-009 is now ready.
- On 2026-06-19, PR #30 was opened for GL-006; issue #6 is in PR and no longer
  listed as ready.
