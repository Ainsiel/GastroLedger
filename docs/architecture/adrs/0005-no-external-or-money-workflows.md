# ADR-0005: No External APIs Or Real-Money Workflows In V1

```text
status = proposed
```

## Decision

V1 uses local authentication, in-app notifications, CSV/manual data exchange and
informational monetary values. It does not process subscriptions, payments,
settlements, accounting, payroll, invoices, collections or external API calls.

## Consequences

- Sales, cash shifts, supplier adjustments and royalty estimates must use language
  that cannot be mistaken for financial transaction truth.
- Users manually share invitation links and import data.
- Any external integration or real-money lifecycle requires SDD expansion, security
  review and a new ADR.
