# Assumptions And Open Questions

## Accepted Simulation Assumptions

- One tenant represents one restaurant holding, chain or franchise operator.
- A branch belongs to exactly one tenant and may have multiple warehouses.
- Base currency is descriptive; the system performs no currency conversion.
- Ingredients and sub-recipes use decimal quantities with explicit units.
- Menu recipes may reference ingredients and one level of sub-recipe.
- Prepared sub-recipes are stocked as lots and consumed by menu-item sales.
- FEFO applies when expiry exists; FIFO applies otherwise.
- Moving weighted average cost is maintained by branch and ingredient.
- Sales are operational imports or simulations, never payment transactions.
- Tenant users authenticate locally; invitations are shared manually.

## Deferred Questions

| ID | Question | Recommended V1 default | Review trigger |
|---|---|---|---|
| OQ-001 | Must branches use different base currencies? | No | First confirmed multi-currency tenant |
| OQ-002 | Is offline warehouse operation required? | No | Repeated connectivity incidents |
| OQ-003 | Must recipe nesting exceed depth 2? | No | Proven menu model that cannot be represented |
| OQ-004 | Is a dedicated queue required? | No, PostgreSQL jobs | Queue contention or latency breaches |
| OQ-005 | Is a dedicated analytics store required? | No, PostgreSQL projections | Reporting impacts transactional SLOs |
| OQ-006 | Are legal food-safety records required? | Operational evidence only | Regulatory scope is formally added |

## Primary Risks

- Incorrect conversion factors can amplify inventory errors.
- Late or inaccurate sales imports reduce trust in theoretical stock.
- Shared-schema multi-tenancy requires defense-in-depth and continuous tests.
- Recipe or cost recalculation can become a hot path as menus grow.
