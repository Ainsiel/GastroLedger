# Open Decisions

No unresolved decision blocks the proposed V1 architecture. These items are
deliberately deferred until evidence exists.

| Decision | Current default | Evidence that reopens it |
|---|---|---|
| Dedicated message broker | PostgreSQL jobs/outbox | Sustained queue contention or isolation need |
| Analytics warehouse | PostgreSQL projections | Reports breach transactional SLOs |
| Multi-currency | One descriptive base currency per tenant | Confirmed tenant needs conversion |
| Offline mode | Online-only responsive web | Repeated warehouse connectivity failures |
| Recipe depth | Maximum 2 levels | Confirmed model impossible within limit |
| External integrations | None | New approved SDD and API ownership contract |
