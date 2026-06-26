# Security And Multi-Tenancy Architecture

## Trust Boundaries

- Public registration is bounded, rate-limited and cannot select an existing tenant.
- Authenticated browser sessions resolve one current tenant membership.
- FastAPI use cases authorize tenant/branch capability before accessing repositories.
- PostgreSQL RLS enforces tenant context as defense in depth.
- Worker jobs carry an immutable tenant identifier and set RLS context before work.

## Authentication

- Local passwords use a strong adaptive hash.
- Sessions use rotating opaque identifiers stored only as hashes server-side.
- Cookies are secure, HTTP-only and same-site.
- Optional local TOTP and generated recovery codes require no external provider.
- Invitations are hashed, expiring, single-use links shared manually.

## Authorization

Roles grant named capabilities with tenant-wide or branch scope. The backend
evaluates policy for every command and sensitive query. Frontend visibility improves
usability but never grants authority.

## Tenant Isolation Controls

1. Tenant ID is derived from session/job context, not arbitrary request input.
2. Tenant-owned tables require non-null tenant ID.
3. RLS policies deny access without matching transaction context.
4. Repository APIs require tenant context.
5. Cross-tenant probes and worker isolation are permanent integration tests.
6. Audit records capture denied privileged attempts without exposing hidden data.

## Threat Responses

| Threat | Response |
|---|---|
| Cross-tenant access | RLS, scoped policies, opaque not-found behavior and tests |
| Credential abuse | Rate limits, session revocation, optional TOTP and audit |
| CSV abuse | Size/row limits, strict parsing, formula-safe exports and no execution |
| Inventory manipulation | Scoped approval, immutable ledger and audit |
| Duplicate command/import | Idempotency keys and unique constraints |
| Sensitive browser persistence | No credentials or authorization truth in browser storage |
| Injection | Typed validation, parameterized SQL/ORM and output encoding |

No secret values, external identity, email, SMS or payment credentials are required.
