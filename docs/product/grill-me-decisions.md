# Recommended Grill Me Decisions

```text
status = accepted for simulation
decision_mode = user_authorized_recommended_defaults
```

| Question | Recommended answer | Consequence |
|---|---|---|
| How is a company registered? | Self-service company registration creates an active pilot tenant and first administrator | No sales-assisted provisioning required |
| Are subscriptions billed? | No; service tier and limits are internal configuration only | No billing, payment or subscription context |
| How do users authenticate? | Local username/password sessions with optional TOTP | No external identity or email dependency |
| How are invitations delivered? | Administrator generates a time-limited invitation link and shares it outside the system | No email API |
| What is the tenant model? | Shared PostgreSQL database and schema with mandatory `tenant_id` plus RLS defense in depth | Moderate operational cost with strong isolation |
| What is the stock truth? | Immutable inventory movements and lots; balances are projections | Every adjustment remains explainable |
| How are expirations allocated? | FEFO when expiry exists, FIFO otherwise | Better food-safety behavior than PEPS-only allocation |
| How deep can recipes nest? | Menu item -> sub-recipe -> ingredient, maximum depth 2 | Prevents cycles and uncontrolled costing complexity |
| How are costs valued? | Moving weighted average by branch and ingredient; recipe snapshots preserve history | Traceable and practical V1 valuation |
| What happens on stock shortage during sale import? | No negative stock; create an allocation exception for review | Protects ledger integrity |
| How do sales enter? | Manual entry, simulation or bounded CSV import | No POS dependency |
| How are automatic purchase orders handled? | System produces suggestions; a user must create/approve an order | No autonomous commitments |
| Are supplier returns financial? | Record returned quantity and expected supplier adjustment only | No credit-note transaction |
| Is cash management financial? | Record opening float, expected cash aggregate and closing count only | No settlement or payment processing |
| Is payroll calculated? | Report hours, overtime candidates and absences only | No payroll or salary calculation |
| Are royalties charged? | Calculate royalty estimates and manually control ordering holds | No invoices, collections or real debt automation |
| How are alerts delivered? | In-app notifications and dashboards | No email, SMS or push API |
| Architecture style? | Modular monolith with API and worker deployables from one FastAPI codebase | Simple deployment with explicit boundaries |
| Async mechanism? | PostgreSQL job queue and transactional outbox | No broker dependency in V1 |
| Frontend style? | Next.js App Router organized by user capability | Clear route and feature ownership |
