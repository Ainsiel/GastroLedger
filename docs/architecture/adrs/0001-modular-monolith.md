# ADR-0001: Use A Modular Monolith

```text
status = proposed
```

## Decision

Use one modular FastAPI backend codebase with separate API and worker entry points,
one Next.js web application and one PostgreSQL database.

## Rationale

The first version has meaningful domain boundaries but no scale or team evidence
that justifies distributed services. A modular monolith minimizes operational cost
while preserving ownership and future extraction options.

## Consequences

- Cross-context boundaries require architecture tests and public contracts.
- API and worker can deploy independently without duplicating domain code.
- A context may become a service only after measured isolation/deployment need and a
  new ADR.
