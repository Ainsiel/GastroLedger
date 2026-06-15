# Next.js Frontend Architecture

## Route And Feature Ownership

| Route group | Owning feature | Main workflows |
|---|---|---|
| `(public)/register` | onboarding | UC-001 |
| `(app)/settings` | platform-admin | UC-002 to UC-004 |
| `(app)/menu` | menu-engineering | UC-005, UC-006, UC-008 to UC-010 |
| `(app)/procurement` | procurement | UC-007, UC-012 to UC-014 |
| `(app)/inventory` | inventory-production | UC-011, UC-015 to UC-020 |
| `(app)/operations` | store-operations | UC-021 to UC-023 |
| `(app)/control` | control-insights | UC-024, UC-025 |

## Boundaries

- Route files compose pages and load initial server-owned data.
- shadcn/ui-derived primitives and GastroLedger design tokens live under shared
  frontend component paths and contain no domain behavior.
- Server Components are the default for read views and access-sensitive composition.
- Client Components are limited to interactive forms, scanners/count entry, previews
  and pending-state feedback.
- Typed API clients and DTO-to-view mappings live at feature boundaries.
- Visual components never call FastAPI directly.
- Backend remains the final authority for tenant scope, permissions and invariants.
- Visual direction and responsive/accessibility requirements are defined in
  `ui-design-spec.md`.

## State Ownership

| State | Owner |
|---|---|
| Filters, period, branch and pagination | URL |
| Tenant, branch, recipes, balances and report results | FastAPI server state |
| Draft form fields and count-entry interaction | Local client component |
| Long-running import/job status | Server state with bounded polling |
| Session and authorization result | Secure server/session boundary |
| Toasts and temporary dialogs | Local UI state |

No global client store is justified for V1.

## Visible Failure States

Every critical workflow defines loading, empty, unauthorized, stale/conflict,
validation, incomplete and unexpected-error states. Imports and reports never hide
exceptions or incomplete confidence.

## Frontend Contract Tests

- typed contract compatibility against FastAPI OpenAPI;
- feature tests for forms, error normalization and duplicate submission;
- accessibility checks for keyboard and accessible names;
- end-to-end coverage for registration, recipe approval, receiving, count approval,
  sales import and variance report.
