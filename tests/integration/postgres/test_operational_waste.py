from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid4

import psycopg
import pytest
from test_production_batch_ledger import setup_production

from gastroledger_api.modules.inventory_production.public import (
    SubmitWaste,
    WasteConflict,
    WasteIdentity,
    WasteService,
)
from gastroledger_api.technical.postgres_inventory import PostgresInventoryStore


def test_waste_approval_gate_and_compensation_are_atomic(
    postgres_connection: psycopg.Connection[tuple[object, ...]], database_url: str
) -> None:
    operator, warehouse_id, _recipe_id = setup_production(database_url)
    manager_id = uuid4()
    with postgres_connection.transaction():
        lot_id = postgres_connection.execute(
            """select id from inventory_lots
               where tenant_id=%s and warehouse_id=%s
               and ingredient_id is not null""",
            (operator.tenant_id, warehouse_id),
        ).fetchone()[0]
        postgres_connection.execute(
            """insert into platform_users(id,normalized_login,password_hash,created_at)
               values(%s,%s,%s,%s)""",
            (manager_id, f"manager-{manager_id}@example.com", "test", datetime.now(UTC)),
        )
        postgres_connection.execute(
            """insert into platform_memberships(tenant_id,user_id,role)
               values(%s,%s,'branch_manager')""",
            (operator.tenant_id, manager_id),
        )
    service = WasteService(store=PostgresInventoryStore(database_url))
    operator_identity = WasteIdentity(operator.tenant_id, operator.actor_id, "tenant_admin")
    manager_identity = WasteIdentity(operator.tenant_id, str(manager_id), "branch_manager")

    low = service.submit_waste(
        operator_identity,
        SubmitWaste("waste-low", warehouse_id, str(lot_id), "1", "spoilage"),
        correlation_id="low",
    )
    assert low.status == "posted"
    with postgres_connection.transaction():
        postgres_connection.execute("update inventory_lots set unit_cost=25 where id=%s", (lot_id,))
    pending = service.submit_waste(
        operator_identity,
        SubmitWaste("waste-high", warehouse_id, str(lot_id), "4", "damaged batch"),
        correlation_id="pending",
    )
    assert pending.status == "pending_approval"
    with pytest.raises(WasteConflict):
        service.approve_waste(
            operator_identity, pending.waste_id, "approve-self", correlation_id="self"
        )
    posted = service.approve_waste(
        manager_identity, pending.waste_id, "approve-manager", correlation_id="approve"
    )
    corrected = service.correct_waste(
        manager_identity,
        posted.waste_id,
        "correct-manager",
        "entered in error",
        correlation_id="correct",
    )
    assert corrected.status == "corrected"
    repeated_correction = service.correct_waste(
        manager_identity,
        posted.waste_id,
        "correct-manager",
        "Duplicate delivery",
        correlation_id="correct-retry",
    )
    assert repeated_correction.status == "corrected"
    rejected = service.submit_waste(
        operator_identity,
        SubmitWaste("waste-reject", warehouse_id, str(lot_id), "4", "review me"),
        correlation_id="reject-pending",
    )
    rejected = service.reject_waste(
        manager_identity,
        rejected.waste_id,
        "not operational waste",
        correlation_id="reject",
    )
    assert rejected.status == "rejected"

    with postgres_connection.transaction():
        row = postgres_connection.execute(
            """select
              (select count(*) from inventory_waste_records where tenant_id=%s),
              (select count(*) from inventory_transactions
               where tenant_id=%s and source_waste_id is not null),
              (select quantity from inventory_stock_balances where lot_id=%s),
              (select sum(quantity) from inventory_entries e
               join inventory_transactions t on t.id=e.transaction_id
               where t.tenant_id=%s and t.source_waste_id is not null)
            """,
            (operator.tenant_id, operator.tenant_id, lot_id, operator.tenant_id),
        ).fetchone()
    assert row == (3, 3, Decimal("5.0000000000"), Decimal("-1.0000000000"))
