# Architecture Index

```text
status = proposed
style = modular monolith
frontend = Next.js App Router
backend = FastAPI API and worker
database = PostgreSQL
logical_relations = 54
external_api_dependencies = 0
html_diagrams = omitted by user request
```

## Reading Order

1. `architecture-questionnaire.md`
2. `architecture-drivers.md`
3. `skill-selection-plan.md`
4. `architecture-overview.md`
5. `domain/`
6. `dependency-rules.md`, `use-case-boundaries.md`, `port-adapter-map.md`
7. `api/`, `data/`, `frontend/`, `security/`, `testing/`, `operations/`
8. `adrs/`, `backlog/` and `handoff.md`

## Foundation Rule

`architecture-foundation` may later materialize module skeletons, ports, contracts,
composition roots and architecture tests. It must not implement product behavior.
Functional work begins only from approved vertical work orders.
