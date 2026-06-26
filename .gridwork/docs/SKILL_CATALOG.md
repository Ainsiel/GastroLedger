# Skill Catalog

| Skill | Category | Notes |
|---|---|---|
| handoff | handoff | Required only on agent or session transfer. |
| sdd-requirements | requirements | Generates SDD drafts from ideation. |
| backlog-planning | planning | Creates local vertical-slice issue drafts. |
| backlog-management | planning | Maintains backlog visibility and prepares selected tasks for implementation. |
| architecture-foundation-planning | architecture-foundation | Converts approved architecture into an exact minimal materialization plan. |
| project-scaffolding | architecture-foundation | Creates approved minimal executable structure without business behavior. |
| module-boundary-enforcement | architecture-testing | Creates tests for approved dependency and module boundaries. |
| contract-first-boundaries | architecture-foundation | Materializes only required contracts with known consumers. |
| composition-root-wiring | architecture-foundation | Assembles approved components outside domain behavior. |
| architecture-conformance-verification | architecture-testing | Verifies structure against approved architecture and anti-speculation rules. |
| frontend-architecture-design | frontend-architecture | Defines feature boundaries, route ownership and public surfaces. |
| frontend-state-strategy | frontend-architecture | Assigns URL, server, local, global and persistent state ownership. |
| frontend-api-contract-consumption | frontend-architecture | Defines typed API consumption, DTO mapping and frontend error behavior. |
| frontend-testing-strategy | testing | Defines frontend behavior, integration, contract, accessibility and E2E coverage. |
| work-order-branch-lifecycle | git | Binds one work order to one feature branch from develop. |
| pull-request-lifecycle | github | Governs feature and release PR state through approved merge. |
| ci-status-evaluation | cicd | Evaluates required checks for the exact PR head SHA. |
| release-promotion | release | Coordinates verified promotion from develop to main. |
| deployment-verification | deployment | Observes production deployment and smoke-check evidence. |
| github-actions-cicd | cicd | Draft-only by default. |
| github-cli | tooling | Governed `gh` usage. |
| github-issue-publisher | github | Publishes approved issue drafts with approval. |
| github-issue-discovery | github | Read-only discovery and normalization. |
| architecture-grill-me | architecture | Adaptive interview and optional skill selection. |
| ubiquitous-language | architecture | Canonical domain terminology and ambiguity control. |
| domain-driven-design | architecture | Strategic and tactical DDD boundaries. |
| clean-architecture | architecture | Dependency direction, ports and adapters. |
| architecture-pattern-selection | architecture | Evidence-based system pattern selection. |
| design-pattern-selection | architecture | Problem-driven local pattern selection. |
| api-contract-design | architecture | Consumer-oriented API and event contracts. |
| relational-data-modeling | architecture | Conceptual, logical and physical relational design. |
| architecture-decision-records | architecture | Consequential decisions and review triggers. |
| html-architecture-diagrams | architecture | Self-contained HTML rendering foundation. |
| c4-html-diagrams | architecture-diagram | Optional context, container, component and dynamic views. |
| erd-html-diagrams | architecture-diagram | Optional MER/ERD conceptual, logical or physical views. |
| uml-html-diagrams | architecture-diagram | Optional sequence, state, activity, class or deployment views. |
| diagnose-bug | diagnosis | Diagnosis only unless used inside an implementation workflow. |
| tdd | implementation | Behavior-first red-green-refactor with vertical tracer bullets. |
| integration-test-design | testing | Technology-agnostic integration boundary and scenario design. |
| integration-testing | testing | Technology-agnostic tests across meaningful real boundaries. |
| git-branch-management | git | Prepares governed Git plans; every write remains gated. |
| github-label-manager | github | Audits predefined labels and prepares approved create plans. |
| gridwork-release-publisher | release | Dry-run release plans by default. |
| monorepo-layout-design | architecture | Defines repository component boundaries and ownership. |
| repository-bootstrap | platform | Creates approved framework scaffolds without business behavior. |
| quality-command-contract | testing | Aligns root local and CI commands. |
| docker-compose-environment-strategy | platform | Defines base Compose plus environment overlays. |
| github-actions-monorepo-ci | cicd | Defines branch-aware monorepo CI gates. |
| github-actions-reusable-workflows | cicd | Extracts reusable component pipelines. |
| changed-scope-detection | cicd | Optimizes feature PR checks only. |
| ci-failure-diagnosis | diagnosis | Produces scoped CI repair handoffs. |
| container-build-and-verification | platform | Builds and smoke-tests containers. |
| github-rulesets-management | github | Plans and applies approved branch protections. |
| github-environments-management | github | Plans and applies approved environments. |
| rollback-planning | deployment | Defines recovery criteria and compatibility. |

## Stack Pack Skills

The `nextjs-springboot-postgresql` stack pack provides:

| Technology | Skills |
|---|---|
| Next.js | `nextjs-frontend-guidance`, `nextjs-app-router-architecture`, `nextjs-auth-session-guidance`, `nextjs-data-fetching-and-cache`, `nextjs-ui-design`, `nextjs-performance`, `nextjs-project-bootstrap`, `nextjs-ci-quality-gates`, `nextjs-container-build`, `nextjs-e2e-testing` |
| Spring Boot | `springboot-backend-guidance`, `springboot-performance`, `springboot-project-bootstrap`, `springboot-ci-quality-gates`, `springboot-migration-testing`, `springboot-container-build`, `springboot-integration-testing` |
| FastAPI | `fastapi-backend-guidance`, `fastapi-performance`, `fastapi-project-bootstrap`, `fastapi-ci-quality-gates`, `fastapi-migration-testing`, `fastapi-container-build`, `fastapi-integration-testing` |
| PostgreSQL | `postgresql-persistence-guidance`, `postgresql-performance`, `postgres-test-environment`, `database-migration-verification` |
| Docker | `dockerfile-authoring`, `docker-compose-local-guidance`, `docker-compose-optimization` |

Stack skills never generate product code during `init`. They may guide or modify confirmed scoped files only inside the active agent and workflow permissions.

For frontend-bearing GastroLedger work, the relevant frontend skills operate under
`frontend-delivery-policy.md`: approved UI sources, shadcn/ui consistency,
responsive/accessibility evidence and visual QA are mandatory.
