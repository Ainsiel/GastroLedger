from datetime import date
from decimal import Decimal
from uuid import uuid4

import psycopg
import pytest

from gastroledger_api.modules.menu_engineering.public import (
    CreateIngredient,
    CreateUnit,
    MenuCatalogService,
)
from gastroledger_api.modules.platform_organization.application.registration import (
    RegisterTenant,
    RegistrationCommand,
)
from gastroledger_api.modules.platform_organization.application.security import (
    ScryptPasswordHasher,
    SessionTokenIssuer,
)
from gastroledger_api.modules.platform_organization.public import (
    CreateWarehouse,
    OperatingIdentity,
    OperatingScopeService,
)
from gastroledger_api.modules.procurement.public import (
    CreateSupplier,
    CreateSupplierReceipt,
    CreateSupplierReceiptLine,
    ProcurementReceiptService,
    ProcurementService,
    SupplierIdentity,
)
from gastroledger_api.technical.postgres_menu import PostgresMenuCatalogStore
from gastroledger_api.technical.postgres_platform import PostgresPlatformStore
from gastroledger_api.technical.postgres_procurement import PostgresProcurementStore


class NoOpenMovements:
    def has_open_movements(self, _identity, _warehouse_id) -> bool:
        return False


def setup_receiving(database_url: str) -> tuple[OperatingIdentity, str, str, str, str]:
    slug = f"receipt-{uuid4().hex}"
    registration = RegisterTenant(
        store=PostgresPlatformStore(database_url),
        password_hasher=ScryptPasswordHasher(),
        session_tokens=SessionTokenIssuer(),
    ).execute(
        RegistrationCommand(
            tenant_name="Receipt Tenant",
            tenant_slug=slug,
            admin_email=f"{slug}@example.com",
            password="StrongPassword123",
            branch_name="Main",
            branch_code="MAIN",
        )
    )
    identity = OperatingIdentity(
        registration.tenant_id, registration.actor_id, "tenant_admin"
    )
    catalog = MenuCatalogService(store=PostgresMenuCatalogStore(database_url))
    unit = catalog.create_unit(
        identity,
        CreateUnit(name="Case", code=f"case-{uuid4().hex[:6]}", dimension="count"),
        correlation_id="unit",
    )
    ingredient = catalog.create_ingredient(
        identity,
        CreateIngredient(
            name="Tomatoes",
            code=f"tomatoes-{uuid4().hex[:6]}",
            purchase_unit_id=unit.unit_id,
            consumption_unit_id=unit.unit_id,
            shelf_life_days=10,
            critical_stock_quantity="1",
        ),
        correlation_id="ingredient",
    )
    procurement = ProcurementService(store=PostgresProcurementStore(database_url))
    supplier = procurement.create_supplier(
        SupplierIdentity(identity.tenant_id, identity.actor_id, identity.role),
        CreateSupplier(name="Local Farm", code=f"farm-{uuid4().hex[:6]}"),
        correlation_id="supplier",
    )
    warehouse = OperatingScopeService(
        store=PostgresPlatformStore(database_url),
        movement_guard=NoOpenMovements(),
    ).create_warehouse(
        identity,
        CreateWarehouse(
            branch_id=registration.branch_id,
            name="Receiving",
            code=f"receiving-{uuid4().hex[:6]}",
            warehouse_type="general",
        ),
        correlation_id="warehouse",
    )
    return (
        identity,
        supplier.supplier_id,
        warehouse.warehouse_id,
        ingredient.ingredient_id,
        unit.unit_id,
    )


def receipt_command(
    supplier_id: str,
    warehouse_id: str,
    ingredient_id: str,
    unit_id: str,
    *,
    key: str,
    lot_code: str,
    temperature: str = "4",
) -> CreateSupplierReceipt:
    return CreateSupplierReceipt(
        idempotency_key=key,
        order_reference="PO-SEEDED-1",
        supplier_id=supplier_id,
        warehouse_id=warehouse_id,
        received_on=date.today(),
        lines=(
            CreateSupplierReceiptLine(
                ingredient_id=ingredient_id,
                purchase_unit_id=unit_id,
                lot_code=lot_code,
                ordered_quantity="10",
                delivered_quantity="6",
                unit_cost="2.50",
                expiry_date=date(2026, 12, 31),
                temperature=temperature,
                minimum_temperature="1",
                maximum_temperature="6",
                tolerance_percent="5",
            ),
        ),
    )


def test_partial_receipt_is_atomic_and_retry_is_idempotent(
    postgres_connection: psycopg.Connection[tuple[object, ...]],
    database_url: str,
) -> None:
    identity, supplier_id, warehouse_id, ingredient_id, unit_id = setup_receiving(
        database_url
    )
    service = ProcurementReceiptService(store=PostgresProcurementStore(database_url))
    command = receipt_command(
        supplier_id,
        warehouse_id,
        ingredient_id,
        unit_id,
        key="receive-001",
        lot_code="LOT-001",
    )
    supplier_identity = SupplierIdentity(
        identity.tenant_id, identity.actor_id, identity.role
    )

    first = service.accept_supplier_receipt(
        supplier_identity, command, correlation_id="first"
    )
    retry = service.accept_supplier_receipt(
        supplier_identity, command, correlation_id="retry"
    )

    assert first.status == "partial"
    assert first.lines[0].accepted_quantity == Decimal("6.0000000000")
    assert first.lines[0].remaining_quantity == Decimal("4.0000000000")
    assert retry.receipt_id == first.receipt_id
    assert retry.inventory_transaction_id == first.inventory_transaction_id
    with postgres_connection.transaction():
        counts = postgres_connection.execute(
            """
            select
              (select count(*) from procurement_supplier_receipts where tenant_id = %s),
              (select count(*) from inventory_lots where tenant_id = %s),
              (select count(*) from inventory_transactions where tenant_id = %s),
              (select count(*) from inventory_entries where tenant_id = %s),
              (select sum(quantity) from inventory_stock_balances where tenant_id = %s),
              (select count(*) from control_outbox_events
               where tenant_id = %s and event_type = 'procurement.supplier_receipt.accepted')
            """,
            (identity.tenant_id,) * 6,
        ).fetchone()
    assert counts == (1, 1, 1, 1, Decimal("6.0000000000"), 1)


def test_rejected_or_duplicate_lot_creates_no_second_ledger_entry(
    postgres_connection: psycopg.Connection[tuple[object, ...]],
    database_url: str,
) -> None:
    identity, supplier_id, warehouse_id, ingredient_id, unit_id = setup_receiving(
        database_url
    )
    service = ProcurementReceiptService(store=PostgresProcurementStore(database_url))
    supplier_identity = SupplierIdentity(
        identity.tenant_id, identity.actor_id, identity.role
    )
    service.accept_supplier_receipt(
        supplier_identity,
        receipt_command(
            supplier_id,
            warehouse_id,
            ingredient_id,
            unit_id,
            key="receive-first",
            lot_code="LOT-DUPLICATE",
        ),
        correlation_id="first",
    )
    duplicate = service.accept_supplier_receipt(
        supplier_identity,
        receipt_command(
            supplier_id,
            warehouse_id,
            ingredient_id,
            unit_id,
            key="receive-duplicate",
            lot_code="LOT-DUPLICATE",
        ),
        correlation_id="duplicate",
    )
    hot = service.accept_supplier_receipt(
        supplier_identity,
        receipt_command(
            supplier_id,
            warehouse_id,
            ingredient_id,
            unit_id,
            key="receive-hot",
            lot_code="LOT-HOT",
            temperature="20",
        ),
        correlation_id="hot",
    )

    assert duplicate.status == "rejected"
    assert duplicate.lines[0].rejection_reason == "duplicate_lot"
    assert hot.status == "rejected"
    assert hot.lines[0].rejection_reason == "temperature_out_of_range"
    with postgres_connection.transaction():
        entry_count = postgres_connection.execute(
            "select count(*) from inventory_entries where tenant_id = %s",
            (identity.tenant_id,),
        ).fetchone()[0]
        lot_id = postgres_connection.execute(
            "select id from inventory_lots where tenant_id = %s",
            (identity.tenant_id,),
        ).fetchone()[0]
    assert entry_count == 1
    with pytest.raises(psycopg.errors.CheckViolation):
        with postgres_connection.transaction():
            postgres_connection.execute(
                "update inventory_stock_balances set quantity = -1 where lot_id = %s",
                (lot_id,),
            )
