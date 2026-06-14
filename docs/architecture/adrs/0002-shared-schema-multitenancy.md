# ADR-0002: Shared-Schema Multi-Tenancy With RLS

```text
status = proposed
```

## Decision

Use one PostgreSQL database/shared schema. Every tenant-owned relation has mandatory
`tenant_id`; application transactions set tenant context and PostgreSQL RLS enforces
matching access.

## Alternatives

- Database per tenant: stronger isolation but excessive V1 operations.
- Schema per tenant: migration and connection complexity.
- Application filtering only: simplest but insufficient defense in depth.

## Consequences

- RLS and tenant context are critical infrastructure with permanent tests.
- Global platform operations require narrowly scoped privileged paths.
- Tenant-sharding or isolation model changes require migration planning and an ADR.
