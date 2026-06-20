from datetime import date
from decimal import Decimal
from uuid import uuid4

import psycopg
import pytest

from gastroledger_api.modules.inventory_production.public import (
    PostProductionBatch,
    ProductionIdentity,
    ProductionInsufficientStock,
    ProductionService,
)
from gastroledger_api.modules.menu_engineering.public import (
    CreateIngredient,
    CreateRecipeComponent,
    CreateSubRecipeVersion,
    CreateUnit,
    MenuCatalogService,
    MenuRecipeService,
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
    CreateSupplierOffer,
    CreateSupplierReceipt,
    CreateSupplierReceiptLine,
    ProcurementReceiptService,
    ProcurementService,
    SupplierIdentity,
)
from gastroledger_api.technical.postgres_inventory import PostgresInventoryStore
from gastroledger_api.technical.postgres_menu import PostgresMenuCatalogStore
from gastroledger_api.technical.postgres_platform import PostgresPlatformStore
from gastroledger_api.technical.postgres_procurement import PostgresProcurementStore


class NoOpenMovements:
    def has_open_movements(self, _identity, _warehouse_id) -> bool:
        return False


def setup_production(database_url: str) -> tuple[ProductionIdentity, str, str]:
    slug = f"production-{uuid4().hex}"
    registration = RegisterTenant(
        store=PostgresPlatformStore(database_url),
        password_hasher=ScryptPasswordHasher(),
        session_tokens=SessionTokenIssuer(),
    ).execute(
        RegistrationCommand(
            tenant_name="Production Tenant",
            tenant_slug=slug,
            admin_email=f"{slug}@example.com",
            password="StrongPassword123",
            branch_name="Main",
            branch_code="MAIN",
        )
    )
    operating_identity = OperatingIdentity(
        registration.tenant_id, registration.actor_id, "tenant_admin"
    )
    catalog = MenuCatalogService(store=PostgresMenuCatalogStore(database_url))
    unit = catalog.create_unit(
        operating_identity,
        CreateUnit(name="Kilogram", code=f"kg-{uuid4().hex[:6]}", dimension="mass"),
        correlation_id="unit",
    )
    ingredient = catalog.create_ingredient(
        operating_identity,
        CreateIngredient(
            name="Tomato",
            code=f"tomato-{uuid4().hex[:6]}",
            purchase_unit_id=unit.unit_id,
            consumption_unit_id=unit.unit_id,
            shelf_life_days=10,
            critical_stock_quantity="1",
        ),
        correlation_id="ingredient",
    )
    procurement = ProcurementService(store=PostgresProcurementStore(database_url))
    supplier = procurement.create_supplier(
        SupplierIdentity(registration.tenant_id, registration.actor_id, "tenant_admin"),
        CreateSupplier(name="Farm", code=f"farm-{uuid4().hex[:6]}"),
        correlation_id="supplier",
    )
    procurement.create_supplier_offer(
        SupplierIdentity(registration.tenant_id, registration.actor_id, "tenant_admin"),
        CreateSupplierOffer(
            supplier_id=supplier.supplier_id,
            ingredient_id=ingredient.ingredient_id,
            purchase_unit_id=unit.unit_id,
            price="2",
            currency="USD",
            effective_from=date.today(),
            effective_until=None,
        ),
        correlation_id="offer",
    )
    recipe_service = MenuRecipeService(store=PostgresMenuCatalogStore(database_url))
    recipe = recipe_service.approve_sub_recipe_version(
        operating_identity,
        CreateSubRecipeVersion(
            name="Tomato base",
            code=f"base-{uuid4().hex[:6]}",
            version="v1",
            yield_quantity="2",
            yield_unit_id=unit.unit_id,
            effective_from=date.today(),
            components=(
                CreateRecipeComponent("ingredient", ingredient.ingredient_id, "4", unit.unit_id),
            ),
        ),
        correlation_id="recipe",
    )
    warehouse = OperatingScopeService(
        store=PostgresPlatformStore(database_url), movement_guard=NoOpenMovements()
    ).create_warehouse(
        operating_identity,
        CreateWarehouse(
            branch_id=registration.branch_id,
            name="Kitchen",
            code=f"kitchen-{uuid4().hex[:6]}",
            warehouse_type="kitchen",
        ),
        correlation_id="warehouse",
    )
    ProcurementReceiptService(store=PostgresProcurementStore(database_url)).accept_supplier_receipt(
        SupplierIdentity(registration.tenant_id, registration.actor_id, "tenant_admin"),
        CreateSupplierReceipt(
            idempotency_key="seed-stock",
            order_reference="PO-SEED",
            supplier_id=supplier.supplier_id,
            warehouse_id=warehouse.warehouse_id,
            received_on=date.today(),
            lines=(
                CreateSupplierReceiptLine(
                    ingredient_id=ingredient.ingredient_id,
                    purchase_unit_id=unit.unit_id,
                    lot_code="ING-001",
                    ordered_quantity="6",
                    delivered_quantity="6",
                    unit_cost="2",
                    expiry_date=date(2026, 7, 1),
                    temperature="4",
                    minimum_temperature="1",
                    maximum_temperature="6",
                    tolerance_percent="0",
                ),
            ),
        ),
        correlation_id="receipt",
    )
    return (
        ProductionIdentity(registration.tenant_id, registration.actor_id, "tenant_admin"),
        warehouse.warehouse_id,
        recipe.recipe_version_id,
    )


def test_batch_posts_atomically_and_shortage_rolls_back(
    postgres_connection: psycopg.Connection[tuple[object, ...]], database_url: str
) -> None:
    identity, warehouse_id, recipe_version_id = setup_production(database_url)
    service = ProductionService(store=PostgresInventoryStore(database_url))

    posted = service.post_batch(
        identity,
        PostProductionBatch(
            idempotency_key="production-001",
            batch_number="BATCH-001",
            warehouse_id=warehouse_id,
            recipe_version_id=recipe_version_id,
            actual_yield="1.5",
            output_lot_code="PREP-001",
            produced_on=date.today(),
            variance_reason="trim loss",
        ),
        correlation_id="production-success",
    )

    assert posted.status == "posted"
    assert posted.expected_yield == Decimal("2.0000000000")
    assert posted.actual_yield == Decimal("1.5")
    assert posted.variance_quantity == Decimal("-0.5000000000")
    assert posted.variance_reason == "trim loss"
    assert posted.consumed_quantity == Decimal("4.0000000000")
    with pytest.raises(ProductionInsufficientStock):
        service.post_batch(
            identity,
            PostProductionBatch(
                idempotency_key="production-002",
                batch_number="BATCH-002",
                warehouse_id=warehouse_id,
                recipe_version_id=recipe_version_id,
                actual_yield="2",
                output_lot_code="PREP-002",
                produced_on=date.today(),
                variance_reason="",
            ),
            correlation_id="production-shortage",
        )

    with postgres_connection.transaction():
        rows = postgres_connection.execute(
            """
            select
              (select count(*) from inventory_production_batches where tenant_id = %s),
              (select count(*) from inventory_transactions
               where tenant_id = %s and transaction_type = 'production'),
              (select count(*) from inventory_lots
               where tenant_id = %s and prepared_recipe_version_id is not null),
              (select count(*) from inventory_lots where tenant_id = %s and lot_code = 'PREP-002'),
              (select quantity from inventory_stock_balances b
               join inventory_lots l on l.id = b.lot_id
               where l.tenant_id = %s and l.lot_code = 'ING-001')
            """,
            (identity.tenant_id,) * 5,
        ).fetchone()
    assert rows == (1, 1, 1, 0, Decimal("2.0000000000"))
