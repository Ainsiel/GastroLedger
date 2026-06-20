from decimal import Decimal
from uuid import uuid4

import psycopg
import pytest
from test_production_batch_ledger import NoOpenMovements, setup_production

from gastroledger_api.modules.inventory_production.public import (
    RequestTransfer,
    TransferConflict,
    TransferIdentity,
    TransferService,
)
from gastroledger_api.modules.platform_organization.public import (
    CreateWarehouse,
    OperatingIdentity,
    OperatingScopeService,
)
from gastroledger_api.technical.postgres_inventory import PostgresInventoryStore
from gastroledger_api.technical.postgres_platform import PostgresPlatformStore


def test_transfer_lifecycle_is_idempotent_and_preserves_lineage(
    postgres_connection: psycopg.Connection[tuple[object, ...]], database_url: str
) -> None:
    production_identity, source_id, _recipe_id = setup_production(database_url)
    with postgres_connection.transaction():
        ingredient_id, unit_id, branch_id = postgres_connection.execute(
            """select i.id, i.consumption_unit_id, w.branch_id
               from menu_ingredients i cross join platform_warehouses w
               where i.tenant_id=%s and w.id=%s limit 1""",
            (production_identity.tenant_id, source_id),
        ).fetchone()
    operating = OperatingIdentity(
        production_identity.tenant_id, production_identity.actor_id, "tenant_admin"
    )
    destination = OperatingScopeService(
        store=PostgresPlatformStore(database_url), movement_guard=NoOpenMovements()
    ).create_warehouse(
        operating,
        CreateWarehouse(
            branch_id=str(branch_id),
            name="Destination",
            code=f"dest-{uuid4().hex[:6]}",
            warehouse_type="general",
        ),
        correlation_id="destination",
    )
    identity = TransferIdentity(
        production_identity.tenant_id, production_identity.actor_id, "tenant_admin"
    )
    service = TransferService(store=PostgresInventoryStore(database_url))
    requested = service.request_transfer(
        identity,
        RequestTransfer(
            transfer_number="TR-001",
            source_warehouse_id=source_id,
            destination_warehouse_id=destination.warehouse_id,
            item_type="ingredient",
            item_id=str(ingredient_id),
            unit_id=str(unit_id),
            requested_quantity="6",
        ),
        correlation_id="request",
    )
    approved = service.approve_transfer(
        identity, requested.transfer_id, "5", correlation_id="approve"
    )
    dispatched = service.dispatch_transfer(
        identity, requested.transfer_id, "dispatch-1", "5", correlation_id="dispatch"
    )
    retry_dispatch = service.dispatch_transfer(
        identity, requested.transfer_id, "dispatch-1", "5", correlation_id="retry"
    )
    received = service.receive_transfer(
        identity,
        requested.transfer_id,
        "receive-1",
        "4",
        "1",
        "damaged in transit",
        correlation_id="receive",
    )
    retry_receipt = service.receive_transfer(
        identity,
        requested.transfer_id,
        "receive-1",
        "4",
        "1",
        "damaged in transit",
        correlation_id="retry-receive",
    )

    assert approved.requested_quantity == Decimal("6.0000000000")
    assert approved.approved_quantity == Decimal("5")
    assert dispatched.dispatched_quantity == Decimal("5")
    assert retry_dispatch.dispatched_quantity == Decimal("5.0000000000")
    assert received.status == "completed"
    assert retry_receipt.received_quantity == Decimal("4.0000000000")
    assert retry_receipt.loss_quantity == Decimal("1.0000000000")
    with pytest.raises(TransferConflict):
        service.receive_transfer(
            identity,
            requested.transfer_id,
            "receive-excess",
            "1",
            "0",
            "",
            correlation_id="excess",
        )
    with postgres_connection.transaction():
        counts = postgres_connection.execute(
            """select
              (select count(*) from inventory_transactions
               where tenant_id=%s and source_transfer_id=%s),
              (select count(*) from inventory_lots
               where tenant_id=%s and source_transfer_id=%s),
              (select sum(quantity) from inventory_stock_balances b
               join inventory_lots l on l.id=b.lot_id
               where l.tenant_id=%s and l.source_transfer_id=%s),
              (select count(*) from inventory_lots
               where tenant_id=%s and source_transfer_id=%s
               and source_lot_id is not null)
            """,
            (identity.tenant_id, requested.transfer_id) * 4,
        ).fetchone()
    assert counts == (2, 1, Decimal("4.0000000000"), 1)
