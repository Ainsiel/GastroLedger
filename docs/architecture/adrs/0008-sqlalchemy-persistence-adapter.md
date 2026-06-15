# ADR-0008: Use SQLAlchemy 2.0 In PostgreSQL Persistence Adapters

```text
status = accepted
```

## Decision

Use SQLAlchemy 2.0 ORM mappings and synchronous sessions inside PostgreSQL technical
adapters while retaining psycopg as the database driver.

Production SQL migrations remain the schema authority. PostgreSQL roles, `SET LOCAL
ROLE`, tenant context and RLS remain explicit transaction responsibilities and may use
SQLAlchemy textual SQL where ORM constructs do not express the security boundary.

## Rationale

ORM mappings make implemented relations and typed persistence operations easier to
maintain as the modular monolith grows. The selected approach improves persistence
clarity without leaking persistence models into domain, application or transport
contracts.

## Consequences

- SQLAlchemy is an approved backend dependency.
- ORM models live only in technical adapter code.
- Domain and application modules do not import SQLAlchemy.
- Generic CRUD repositories and speculative mappings are forbidden.
- `Base.metadata.create_all()` is forbidden; migrations remain reviewable SQL.
- One session/transaction is used per current store operation.
- Existing PostgreSQL isolation and concurrency integration tests remain permanent.

## Validation

- Registration, duplicate conflict and session identity behavior remain unchanged.
- Runtime identity remains non-privileged.
- RLS denies access without transaction tenant context.
- Architecture tests reject SQLAlchemy imports outside technical persistence code.

## Review Trigger

Revisit if ORM behavior obscures a required PostgreSQL invariant, causes unacceptable
query behavior or cannot safely preserve role and RLS transaction semantics.

