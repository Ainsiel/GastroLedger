from uuid import uuid4

import psycopg


def test_postgres_harness_sets_transaction_local_tenant_context(
    postgres_connection: psycopg.Connection[tuple[object, ...]],
) -> None:
    tenant_id = str(uuid4())

    with postgres_connection.transaction():
        configured = postgres_connection.execute(
            "select set_config('app.current_tenant_id', %s, true)",
            (tenant_id,),
        ).fetchone()
        current = postgres_connection.execute(
            "select current_setting('app.current_tenant_id', true)"
        ).fetchone()

        assert configured == (tenant_id,)
        assert current == (tenant_id,)

