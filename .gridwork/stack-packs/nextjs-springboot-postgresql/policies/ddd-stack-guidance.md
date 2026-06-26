# DDD Stack Guidance

Use DDD language to map:

- bounded contexts;
- aggregates;
- application services;
- domain services;
- repositories;
- DTOs and API contracts;
- persistence boundaries.

Do not impose one architecture. Use the existing project shape unless the architecture workflow decides otherwise.

Recommended mapping:

```text
Next.js route and feature UI -> consumer of application contracts
Spring Boot bounded-context module -> use cases and domain policy
FastAPI router/application module -> consumer and implementation of use-case contracts
PostgreSQL schema ownership -> bounded-context data ownership
Docker Compose -> local runtime mechanism, never a domain boundary
```

Keep transport DTOs, JPA models and UI state distinct from domain concepts when their responsibilities differ.
