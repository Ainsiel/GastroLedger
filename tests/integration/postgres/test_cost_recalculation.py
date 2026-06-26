from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from uuid import uuid4

import psycopg

from gastroledger_api.modules.menu_engineering.public import (
    CreateIngredient,
    CreateMenuItemVersion,
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
from gastroledger_api.modules.platform_organization.public import OperatingIdentity
from gastroledger_api.modules.procurement.public import (
    CreateSupplier,
    CreateSupplierOffer,
    ProcurementService,
    SupplierIdentity,
)
from gastroledger_api.technical.postgres_cost_projection import (
    PostgresCostRecalculationStore,
)
from gastroledger_api.technical.postgres_menu import PostgresMenuCatalogStore
from gastroledger_api.technical.postgres_platform import PostgresPlatformStore
from gastroledger_api.technical.postgres_procurement import PostgresProcurementStore
from gastroledger_worker.cost_recalculation import CostRecalculationWorker


def registered_admin(database_url: str) -> OperatingIdentity:
    slug = f"projection-{uuid4().hex}"
    result = RegisterTenant(
        store=PostgresPlatformStore(database_url),
        password_hasher=ScryptPasswordHasher(),
        session_tokens=SessionTokenIssuer(),
    ).execute(
        RegistrationCommand(
            tenant_name="Projection Tenant",
            tenant_slug=slug,
            admin_email=f"{slug}@example.com",
            password="StrongPassword123",
            branch_name="Main",
            branch_code="MAIN",
        )
    )
    return OperatingIdentity(result.tenant_id, result.actor_id, "tenant_admin")


def add_offer(
    database_url: str,
    identity: OperatingIdentity,
    ingredient_id: str,
    unit_id: str,
    *,
    price: str,
) -> None:
    procurement = ProcurementService(store=PostgresProcurementStore(database_url))
    supplier = procurement.create_supplier(
        SupplierIdentity(identity.tenant_id, identity.actor_id, identity.role),
        CreateSupplier(name=f"Supplier {price}", code=f"supplier-{uuid4().hex[:8]}"),
        correlation_id=f"supplier-{price}",
    )
    procurement.create_supplier_offer(
        SupplierIdentity(identity.tenant_id, identity.actor_id, identity.role),
        CreateSupplierOffer(
            supplier_id=supplier.supplier_id,
            ingredient_id=ingredient_id,
            purchase_unit_id=unit_id,
            price=price,
            currency="USD",
            effective_from=date.today(),
            effective_until=None,
        ),
        correlation_id=f"offer-{price}",
    )


def test_offer_outbox_coalesces_and_recalculates_affected_recipe_costs(
    postgres_connection: psycopg.Connection[tuple[object, ...]],
    database_url: str,
) -> None:
    identity = registered_admin(database_url)
    catalog = MenuCatalogService(store=PostgresMenuCatalogStore(database_url))
    unit = catalog.create_unit(
        identity,
        CreateUnit(name="Kilogram", code=f"kg-{uuid4().hex[:6]}", dimension="mass"),
        correlation_id="unit",
    )
    ingredient = catalog.create_ingredient(
        identity,
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
    add_offer(database_url, identity, ingredient.ingredient_id, unit.unit_id, price="3.50")
    recipes = MenuRecipeService(store=PostgresMenuCatalogStore(database_url))
    sub_recipe = recipes.approve_sub_recipe_version(
        identity,
        CreateSubRecipeVersion(
            name="Tomato base",
            code=f"tomato-base-{uuid4().hex[:6]}",
            version="v1",
            yield_quantity="2",
            yield_unit_id=unit.unit_id,
            effective_from=date.today(),
            components=(
                CreateRecipeComponent("ingredient", ingredient.ingredient_id, "4", unit.unit_id),
            ),
        ),
        correlation_id="sub-recipe",
    )
    menu_item = recipes.approve_menu_item_version(
        identity,
        CreateMenuItemVersion(
            name="Tomato bowl",
            code=f"tomato-bowl-{uuid4().hex[:6]}",
            version="v1",
            yield_quantity="1",
            yield_unit_id=unit.unit_id,
            effective_from=date.today(),
            components=(
                CreateRecipeComponent("sub_recipe", sub_recipe.recipe_id, "1", unit.unit_id),
            ),
        ),
        correlation_id="menu-item",
    )
    add_offer(database_url, identity, ingredient.ingredient_id, unit.unit_id, price="2.00")

    with postgres_connection.transaction():
        queued = postgres_connection.execute(
            """
            select count(*) from control_jobs
            where tenant_id = %s and status = 'queued'
            """,
            (identity.tenant_id,),
        ).fetchone()[0]
        outbox = postgres_connection.execute(
            "select count(*) from control_outbox_events where tenant_id = %s",
            (identity.tenant_id,),
        ).fetchone()[0]
    assert queued == 1
    assert outbox == 2

    worker = CostRecalculationWorker(
        store=PostgresCostRecalculationStore(database_url),
        worker_id="integration-worker",
    )
    assert worker.run_once()

    listed = recipes.list_menu_items(identity)
    projected = next(
        item for item in listed if item.recipe_version_id == menu_item.recipe_version_id
    )
    assert projected.cost_snapshot.total_cost == Decimal("4.0000000000")
    assert projected.cost_projection is not None
    assert projected.cost_projection.status == "current"

    with postgres_connection.transaction():
        job_status = postgres_connection.execute(
            "select status from control_jobs where tenant_id = %s",
            (identity.tenant_id,),
        ).fetchone()[0]
        event_statuses = postgres_connection.execute(
            "select distinct status from control_outbox_events where tenant_id = %s",
            (identity.tenant_id,),
        ).fetchall()
        projection_count = postgres_connection.execute(
            "select count(*) from menu_cost_projection_snapshots where tenant_id = %s",
            (identity.tenant_id,),
        ).fetchone()[0]
    assert job_status == "completed"
    assert event_statuses == [("processed",)]
    assert projection_count == 2


def test_expired_lease_retries_without_rolling_back_source_or_prior_snapshot(
    postgres_connection: psycopg.Connection[tuple[object, ...]],
    database_url: str,
) -> None:
    identity = registered_admin(database_url)
    catalog = MenuCatalogService(store=PostgresMenuCatalogStore(database_url))
    unit = catalog.create_unit(
        identity,
        CreateUnit(name="Each", code=f"each-{uuid4().hex[:6]}", dimension="count"),
        correlation_id="unit",
    )
    ingredient = catalog.create_ingredient(
        identity,
        CreateIngredient(
            name="Bread",
            code=f"bread-{uuid4().hex[:6]}",
            purchase_unit_id=unit.unit_id,
            consumption_unit_id=unit.unit_id,
            shelf_life_days=5,
            critical_stock_quantity="1",
        ),
        correlation_id="ingredient",
    )
    add_offer(database_url, identity, ingredient.ingredient_id, unit.unit_id, price="1.50")
    recipe_service = MenuRecipeService(store=PostgresMenuCatalogStore(database_url))
    recipe = recipe_service.approve_sub_recipe_version(
        identity,
        CreateSubRecipeVersion(
            name="Bread base",
            code=f"bread-base-{uuid4().hex[:6]}",
            version="v1",
            yield_quantity="1",
            yield_unit_id=unit.unit_id,
            effective_from=date.today(),
            components=(
                CreateRecipeComponent("ingredient", ingredient.ingredient_id, "2", unit.unit_id),
            ),
        ),
        correlation_id="recipe",
    )
    with postgres_connection.transaction():
        postgres_connection.execute(
            """
            update control_jobs
            set status = 'leased', lease_until = %s,
                payload = jsonb_build_object('ingredientId', 'not-a-uuid')
            where tenant_id = %s
            """,
            (datetime.now(UTC) - timedelta(minutes=1), identity.tenant_id),
        )

    worker = CostRecalculationWorker(
        store=PostgresCostRecalculationStore(database_url),
        worker_id="retry-worker",
    )
    assert worker.run_once()

    with postgres_connection.transaction():
        offer_count = postgres_connection.execute(
            "select count(*) from procurement_supplier_offers where tenant_id = %s",
            (identity.tenant_id,),
        ).fetchone()[0]
        prior_cost = postgres_connection.execute(
            "select total_cost from menu_cost_snapshots where recipe_version_id = %s",
            (recipe.recipe_version_id,),
        ).fetchone()[0]
        job = postgres_connection.execute(
            "select status, attempts, last_error from control_jobs where tenant_id = %s",
            (identity.tenant_id,),
        ).fetchone()
        event = postgres_connection.execute(
            "select status, attempts, last_error from control_outbox_events where tenant_id = %s",
            (identity.tenant_id,),
        ).fetchone()
    assert offer_count == 1
    assert prior_cost == Decimal("3.0000000000")
    assert job[0] == "queued"
    assert job[1] == 1
    assert "badly formed" in job[2]
    assert event[0] == "pending"
    assert event[1] == 1
