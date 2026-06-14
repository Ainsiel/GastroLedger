# GastroLedger

GastroLedger is bootstrapped as a modular-monolith monorepo:

- `apps/web`: Next.js App Router web entry point.
- `apps/api`: FastAPI HTTP entry point and reusable backend runtime modules.
- `apps/worker`: separate worker entry point that imports modules from `apps/api`.
- `packages/api-contract`: transport-only TypeScript contracts.
- `tests/integration`: cross-entry-point technical integration tests.
- `tests/e2e`: reserved for approved visible workflows.
- `infra/compose`: base Compose contract and environment overlays.
- `infra/containers`: container build definitions.

Repository bootstrap intentionally contains no business use-case behavior.

## Prerequisites

- Node.js `22.x`
- npm `10.x`
- Docker Engine `28.x` or compatible
- Docker Compose `2.35+`

Python `3.13` runs through the repository containers, so a host Python installation is
not required.

## Root Commands

```text
npm run bootstrap
npm run lint
npm test
npm run test:migrations
npm run test:e2e:critical
npm run build
npm run dev
npm start
npm run compose:config
npm run compose:config:integration
```

All Compose-backed commands use `infra/compose/.env.example`, which contains local
localhost-only, non-secret values. Supply shared-environment credentials outside
version control.

`npm run test:e2e:critical` expects the isolated integration runtime on ports `58000`
and `53000`; CI starts it through `compose.integration.yaml`.
