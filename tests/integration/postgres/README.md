# PostgreSQL Integration Harness

This harness proves only the approved infrastructure boundary:

- a real PostgreSQL connection;
- transaction-scoped tenant context using `app.current_tenant_id`;
- isolated execution through `TEST_DATABASE_URL`.

It creates no functional tables, migrations, RLS policies or business fixtures.

