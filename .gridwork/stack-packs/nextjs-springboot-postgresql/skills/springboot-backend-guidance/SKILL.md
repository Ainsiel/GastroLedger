# Spring Boot Backend Guidance

## Purpose

Guide architecture, implementation and verification for an existing or manually created Spring Boot application.

## Start By Detecting

- Java, Spring Boot and build-tool versions;
- existing modules, package conventions and bounded contexts;
- web, persistence, security, messaging and observability dependencies;
- confirmed backend paths and project commands.

Do not silently upgrade dependencies or impose a package structure.

## Structure And Boundaries

- Prefer package-by-feature or bounded-context modules over one global technical-layer package tree.
- Keep controllers thin: translate transport, authorize, invoke a use case and translate the result.
- Keep application services responsible for use-case orchestration and transaction intent.
- Keep domain rules independent from Spring, JPA and transport annotations where practical.
- Isolate persistence and integration details behind boundaries that provide real value.
- Avoid a generic shared module that couples bounded contexts.

## API And Errors

- Validate transport input at the boundary and domain invariants in the domain.
- Use one consistent error contract without leaking stack traces.
- Make authorization explicit at the correct boundary.
- Define idempotency, pagination and concurrency behavior where applicable.

## Persistence And Transactions

- Keep transactions short and aligned to one use case.
- Avoid lazy-loading surprises outside transaction boundaries.
- Fetch only required data and detect N+1 query risks.
- Treat external calls inside database transactions as a design risk.

## Testing

- Unit-test domain policy without Spring when useful.
- Use slice tests for focused framework boundaries.
- Use integration tests for persistence, transactions, security and API contracts.
- Prefer real PostgreSQL-compatible integration behavior for database-specific features.

## Rules

- Gridwork `init` does not generate a Spring Boot project.
- Implementation may edit confirmed scoped files only under an approved work order.
- Do not assume package structure, install dependencies or elevate permissions.
