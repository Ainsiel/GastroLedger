# Observability And Data Exit

## Observability

- Every request, command, job and outbox event carries a correlation identifier.
- Metrics cover request latency/errors, job age/retries, outbox backlog, allocation
  exceptions, import status and cost snapshot freshness.
- Logs include tenant-safe identifiers but never credentials, tokens or CSV content.
- Operational dashboards expose incomplete reports and failed jobs to authorized
  administrators.

## Tenant Data Exit

An authorized tenant administrator can generate a local export containing:

- tenant settings, branches, warehouses, users and scoped roles;
- units, ingredients, recipe versions and cost snapshots;
- suppliers, orders, receipts and returns;
- lots, immutable inventory entries, production, transfers, waste and counts;
- sales records, cash shifts, schedules, attendance and royalty estimates;
- audit records relevant to the tenant.

Export uses documented CSV/JSON files and a relationship manifest. It is downloaded
by the authorized user and never transmitted to a third party by the system.
