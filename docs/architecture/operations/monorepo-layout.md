# Proposed Monorepo Layout

```text
apps/
  web/                 Next.js application
  api/                 FastAPI HTTP entry point and backend modules
  worker/              FastAPI backend worker entry point, no duplicated domain code
packages/
  api-contract/        Generated/validated transport contract artifacts only
tests/
  integration/         Cross-module and PostgreSQL integration suites
  e2e/                 Critical visible workflows
infra/
  compose/             Base and environment overlays
  containers/          Container build definitions
docs/
  sdd/
  architecture/
  adr/
```

## Ownership Rules

- Backend business modules remain owned by `apps/api`; `apps/worker` imports their
  public application composition, not copies.
- `packages/api-contract` contains no domain behavior.
- Frontend features do not import backend source.
- Infrastructure contains no business rules.
- Actual directories are created only by approved `repository-bootstrap`.
