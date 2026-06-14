# Backlog Snapshot

```text
run_id = backlog-management-20260614-01
generated_at = 2026-06-14T18:32:18-04:00
sources = docs/sdd, docs/architecture, repository structure, GitHub read-only audit
status = local draft only
github_issues_observed = 0
```

## Summary

| Readiness | Count |
|---|---:|
| Ready candidate | 1 |
| Defined, blocked by dependencies | 22 |
| Needs requirement refinement | 0 |
| Published | 0 |

The repository already contains the bootstrap, architecture foundation, delivery
infrastructure, six backend module boundaries, frontend feature boundaries and an
isolated PostgreSQL harness. No product behavior or functional tables exist yet.

## Items

| ID | Outcome | Primary context | Trace | Readiness | Dependencies |
|---|---|---|---|---|---|
| GL-001 | Register a tenant and prove isolation | Platform & Organization | UC-001 | Ready tracer | Foundation |
| GL-002 | Manage local users, invitations and scoped roles | Platform & Organization | UC-003 | Blocked | GL-001 |
| GL-003 | Configure tenant settings, branches and warehouses | Platform & Organization | UC-002, UC-004 | Blocked | GL-001 |
| GL-004 | Manage units and ingredient catalog | Menu Engineering | UC-005, UC-006 | Blocked | GL-001, GL-003 |
| GL-005 | Manage suppliers and effective-dated offers | Procurement | UC-007 | Blocked | GL-004 |
| GL-006 | Approve versioned sub-recipes | Menu Engineering | UC-008 | Blocked | GL-004 |
| GL-007 | Approve menu items and branch margin | Menu Engineering | UC-009 | Blocked | GL-003, GL-006 |
| GL-008 | Recalculate recipe cost snapshots asynchronously | Menu Engineering | UC-010 | Blocked | GL-007 |
| GL-009 | Receive a supplier delivery into the inventory ledger | Procurement | UC-013 | Blocked | GL-003, GL-004, GL-005 |
| GL-010 | Post a production batch and prepared lot | Inventory & Production | UC-011 | Blocked | GL-006, GL-009 |
| GL-011 | Complete a stock transfer lifecycle | Inventory & Production | UC-015 to UC-017 | Blocked | GL-003, GL-009 |
| GL-012 | Record operational waste with approval evidence | Inventory & Production | UC-018 | Blocked | GL-009 |
| GL-013 | Create and acknowledge expiry alerts | Inventory & Production | UC-019 | Blocked | GL-008, GL-009 |
| GL-014 | Perform a blind count and reconcile variance | Inventory & Production | UC-020 | Blocked | GL-002, GL-009 |
| GL-015 | Import sales and resolve allocation exceptions | Store Operations | UC-021 | Blocked | GL-007, GL-008, GL-009 |
| GL-016 | Apply manual ordering holds | Control & Insights | UC-024-A/F | Blocked | GL-002, GL-003 |
| GL-017 | Create approved purchase orders | Procurement | UC-012 | Blocked | GL-005, GL-016 |
| GL-018 | Record supplier return and expected adjustment | Procurement | UC-014 | Blocked | GL-009 |
| GL-019 | Reconcile an operational cash shift | Store Operations | UC-022 | Blocked | GL-002, GL-003 |
| GL-020 | Plan shifts and record attendance | Store Operations | UC-023 | Blocked | GL-002, GL-003 |
| GL-021 | Calculate non-financial royalty estimates | Control & Insights | UC-024-S | Blocked | GL-008, GL-015 |
| GL-022 | Analyze cost variance and menu profitability | Control & Insights | UC-025 | Blocked | GL-008, GL-009, GL-014, GL-015, GL-021 |
| GL-023 | Export tenant data in open formats | Platform & Organization | FR-032, IT-025 | Blocked | Full trusted-data path |

## Tracer Slice

`GL-001` is the initial tracer. It proves the highest-risk path before broader
feature work:

```text
Next.js registration -> FastAPI command -> tenant aggregate -> PostgreSQL transaction
-> RLS tenant context -> local session -> isolated authenticated read
```

It must establish production migrations for the minimum Platform & Organization
relations, RLS, transaction-scoped tenant context, password/session security,
transport contracts, visible registration states and cross-tenant integration
evidence.

## Missing Work And Gaps

- GitHub currently has no issues and none of the approved Gridwork labels.
- Exact endpoint paths and DTO field names must be selected inside each approved
  work order while preserving the existing public module boundaries.
- The approved documents define complete behavior, but performance baselines remain
  deferred until representative data exists.
- `GL-023` is intentionally last because a complete export must cover the accepted
  V1 source facts without external transmission.

## Source Conflicts And Freshness

- The architecture backlog groups work into ten broad slices. These drafts preserve
  its sequence but split large lifecycles into implementable outcomes.
- ADR files have documentary status `proposed`, but the user explicitly supplied
  them as approved workflow sources.
- GitHub was inspected read-only on 2026-06-14: zero issues and only default labels
  were present.
