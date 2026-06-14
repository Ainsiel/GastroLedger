# Compose Environment Plan

## Services

| Service | Purpose | Required profiles/overlays |
|---|---|---|
| `web` | Next.js web | develop, qa, production-like |
| `api` | FastAPI HTTP API | develop, qa, production-like |
| `worker` | Jobs/outbox processing | develop, qa, production-like |
| `postgres` | Transactional database | all |
| `migrate` | One-shot migration verification/application | qa, production-like |

## Rules

- One base Compose contract defines networks, health checks and service names.
- Development, QA and production-like differences use overlays, not profiles alone.
- Integration suites receive isolated PostgreSQL ownership.
- Secrets are injected at runtime and no values are committed.
- Compose is the local and test contract; it is not automatically the production
  orchestrator.
- No external API service, broker, Redis or object store is required for V1.

Exact filenames and commands are deferred until bootstrap confirms repository
conventions.
