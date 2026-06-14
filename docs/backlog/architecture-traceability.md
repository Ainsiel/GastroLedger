# Architecture Traceability

Every draft also inherits the modular-monolith and dependency constraints in
`docs/architecture/adrs/0001-modular-monolith.md`,
`docs/architecture/dependency-rules.md` and
`docs/architecture/use-case-boundaries.md`.

| Issue | Approved architecture evidence |
|---|---|
| GL-001 | `security/security-architecture.md`, `data/data-model-design.md`, `frontend/frontend-architecture.md`, ADR-0002 |
| GL-002 | `security/security-architecture.md`, `data/data-model-design.md`, `frontend/frontend-architecture.md` |
| GL-003 | `domain/bounded-contexts.md`, `data/data-model-design.md`, `frontend/frontend-architecture.md` |
| GL-004 | `domain/bounded-contexts.md`, `data/data-model-design.md`, `port-adapter-map.md` |
| GL-005 | `domain/bounded-contexts.md`, `domain/context-map.md`, `data/data-model-design.md` |
| GL-006 | `domain/aggregate-design.md`, `data/data-model-design.md`, ADR-0004 |
| GL-007 | `domain/aggregate-design.md`, `frontend/frontend-architecture.md`, ADR-0004 |
| GL-008 | `port-adapter-map.md`, `data/data-model-design.md`, ADR-0006 |
| GL-009 | `domain/context-map.md`, `port-adapter-map.md`, `data/data-model-design.md`, ADR-0003 |
| GL-010 | `port-adapter-map.md`, `data/data-model-design.md`, ADR-0003, ADR-0004 |
| GL-011 | `domain/aggregate-design.md`, `data/data-model-design.md`, ADR-0003 |
| GL-012 | `domain/aggregate-design.md`, `data/data-model-design.md`, ADR-0003 |
| GL-013 | `data/data-model-design.md`, `port-adapter-map.md`, ADR-0006 |
| GL-014 | `security/security-architecture.md`, `data/data-model-design.md`, ADR-0003 |
| GL-015 | `domain/context-map.md`, `port-adapter-map.md`, `data/data-model-design.md`, ADR-0003, ADR-0004, ADR-0006 |
| GL-016 | `domain/context-map.md`, `port-adapter-map.md`, `security/security-architecture.md` |
| GL-017 | `domain/context-map.md`, `data/data-model-design.md`, `security/security-architecture.md` |
| GL-018 | `domain/context-map.md`, `data/data-model-design.md`, ADR-0003 |
| GL-019 | `security/security-architecture.md`, `data/data-model-design.md`, ADR-0005 |
| GL-020 | `security/security-architecture.md`, `data/data-model-design.md`, ADR-0005 |
| GL-021 | `domain/context-map.md`, `data/data-model-design.md`, ADR-0005 |
| GL-022 | `domain/context-map.md`, `data/data-model-design.md`, `frontend/frontend-architecture.md`, `testing/integration-test-strategy.md` |
| GL-023 | `operations/observability-and-data-exit.md`, `security/security-architecture.md`, `data/data-model-design.md`, ADR-0005 |

ADR references in the table resolve under `docs/architecture/adrs/`. Issue
frontmatter owns requirement, use-case, flow, test-case and dependency traceability.
