# FastAPI Backend Guidance

## Purpose

Guide architecture, implementation and verification for an existing FastAPI service
while respecting its Python tooling, conventions and confirmed paths.

## Start By Detecting

- Python, FastAPI, Pydantic and ASGI server versions;
- dependency and environment tooling such as uv, Poetry or pip;
- application factory, router, dependency injection and lifespan conventions;
- persistence, migration, auth, background-task and test tooling;
- confirmed backend paths and project commands.

Do not silently change dependency tooling, application layout or Pydantic conventions.

## Structure And Boundaries

- Keep routers focused on transport, authorization and use-case invocation.
- Keep business rules independent from FastAPI, request models and persistence models.
- Use dependency injection for real boundaries such as authentication, transactions
  and external services, not as a replacement for clear application design.
- Separate public request/response schemas from domain and persistence models when
  their responsibilities differ.
- Keep async and sync boundaries explicit; avoid blocking work on the event loop.
- Use lifespan management for resources with clear startup and shutdown ownership.

## Contracts And Errors

- Define response models and status codes intentionally.
- Validate transport input at the boundary and domain invariants in the domain.
- Use one safe error contract without leaking traces or internal details.
- Make authorization, idempotency, pagination and concurrency behavior explicit.

## Persistence And Background Work

- Align transaction scope with one use case and keep it short.
- Avoid sharing unsafe sessions or mutable request state.
- Define ownership, retries, failure reporting and idempotency for background tasks.
- Treat external calls inside database transactions as a design risk.

## Testing

- Use `integration-testing` for meaningful router/application/persistence boundaries.
- Prefer public HTTP/ASGI behavior over testing internal function call order.
- Verify dependency overrides are scoped and restored.
- Test lifespan, error, authorization and transaction behavior when relevant.

## Rules

- Gridwork `init` does not generate a FastAPI project.
- Implementation may edit confirmed scoped files only under an approved work order.
- Do not install dependencies, assume paths or elevate permissions.

