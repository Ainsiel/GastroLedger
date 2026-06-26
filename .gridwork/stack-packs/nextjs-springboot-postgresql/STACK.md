# Next.js + Spring Boot/FastAPI + PostgreSQL Stack Pack

## Purpose

Provide guidance for agents working in projects that use:

```text
frontend = Next.js
backend = Spring Boot or FastAPI
database = PostgreSQL
local_environment = Docker Compose recommended
architecture_style = DDD + vertical slices
```

## Rules

- `gridwork init` installs skill definitions only and does not generate product code.
- Approved bootstrap skills may create confirmed framework scaffolds only inside `repository-bootstrap`.
- During an approved implementation work order, stack skills may create or modify confirmed scoped product files.
- Path hints are hints, not permissions.
- Stack skills do not elevate permissions.
- The orchestrator must detect or ask for real project paths before AFK work.
- Stack versions and existing project conventions must be detected before recommendations.

## Vertical Slice Preference

When feasible, issues should include UI, API/application behavior, domain behavior, persistence changes and tests in one independently verifiable slice.

## Skills

```text
Next.js = frontend guidance, App Router architecture, auth/session, data/cache, UI design, performance, bootstrap, CI, container, E2E
Spring Boot = backend guidance, performance, bootstrap, CI, migrations, container, integration
FastAPI = backend guidance, performance, bootstrap, CI, migrations, container, integration
PostgreSQL = persistence guidance, performance, isolated test environment, migration verification
Docker = Dockerfile authoring, Compose local guidance, Compose optimization
```
