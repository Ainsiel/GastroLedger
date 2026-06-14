# Quality Attributes

| ID | Attribute | Scenario and measure |
|---|---|---|
| QA-001 | Tenant isolation | A cross-tenant identifier probe returns no data and creates a security audit signal in 100% of tests. |
| QA-002 | Inventory integrity | Every committed balance change references one immutable movement; no accepted command creates negative stock. |
| QA-003 | Cost consistency | A cost-impacting receipt or yield change updates affected recipe projections within 5 minutes. |
| QA-004 | Import reliability | A repeated CSV import with the same idempotency key creates no duplicate sales or movements. |
| QA-005 | Performance | Common branch dashboards respond within 2 seconds at p95 for the initial target of 100 branches per tenant. |
| QA-006 | Batch performance | A valid import of 10,000 sale lines completes or produces exceptions within 10 minutes. |
| QA-007 | Availability | The monthly service objective is 99.5%, excluding approved maintenance. |
| QA-008 | Recovery | RPO is 15 minutes and RTO is 4 hours, proven by restore rehearsal. |
| QA-009 | Security | Passwords are strongly hashed; sessions are revocable; privileged actions require scoped permission. |
| QA-010 | Auditability | Purchase approval, receiving, adjustment, transfer, waste and hold decisions record actor, time, reason and correlation ID. |
| QA-011 | Accessibility | Critical web workflows meet WCAG 2.1 AA keyboard and accessible-name expectations. |
| QA-012 | Maintainability | Context boundaries and forbidden dependencies are checked before merge. |
| QA-013 | Portability | Local development and integration tests operate without Internet or external APIs. |
| QA-014 | Data exit | A tenant administrator can create a complete documented CSV/JSON export with movement history. |
