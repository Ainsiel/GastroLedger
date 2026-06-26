# Vertical Slice Policy

Prefer issues that can be tested as a complete behavior:

- UI state or route when applicable;
- API/application behavior;
- domain rule;
- persistence or migration when needed;
- tests and acceptance criteria.

For Next.js slices also record:

- affected feature and route;
- Server/Client Component boundary;
- state ownership;
- API consumption and error behavior;
- loading, empty, unauthorized and stale states;
- frontend behavior, accessibility and end-to-end tests.

Avoid splitting work only by frontend/backend/database if that makes the issue hard to verify.
