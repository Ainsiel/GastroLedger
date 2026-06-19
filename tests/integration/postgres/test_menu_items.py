from datetime import date
from decimal import Decimal
from uuid import uuid4

import psycopg
import pytest

from gastroledger_api.modules.menu_engineering.public import (
    CreateBranchMenuPrice,
    CreateIngredient,
    CreateMenuItemVersion,
    CreateRecipeComponent,
    CreateSubRecipeVersion,
    CreateUnit,
    MenuCatalogService,
    MenuRecipeService,
    RecipeMissingCost,
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
from gastroledger_api.technical.postgres_menu import PostgresMenuCatalogStore
from gastroledger_api.technical.postgres_platform import PostgresPlatformStore
from gastroledger_api.technical.postgres_procurement import PostgresProcurementStore


def registered_admin(database_url: str) -> OperatingIdentity:
    slug = f"menu-item-{uuid4().hex}"
    result = RegisterTenant(
        store=PostgresPlatformStore(database_url),
        password_hasher=ScryptPasswordHasher(),
        session_tokens=SessionTokenIssuer(),
    ).execute(
        RegistrationCommand(
            tenant_name="Menu Item Tenant",
            tenant_slug=slug,
            admin_email=f"{slug}@example.com",
            password="StrongPassword123",
            branch_name="Main",
            branch_code="MAIN",
        )
    )
    return OperatingIdentity(
        tenant_id=result.tenant_id,
        actor_id=result.actor_id,
        role="tenant_admin",
    )


def seed_ingredient_with_offer(database_url: str, identity: OperatingIdentity) -> tuple[str, str]:
    catalog = MenuCatalogService(store=PostgresMenuCatalogStore(database_url))
    unit = catalog.create_unit(
        identity,
        CreateUnit(name="Kilogram", code=f"kg-{uuid4().hex[:6]}", dimension="mass"),
        correlation_id="unit-kg",
    )
    ingredient = catalog.create_ingredient(
        identity,
        CreateIngredient(
            name="Tomato",
            code=f"tomato-{uuid4().hex[:6]}",
            purchase_unit_id=unit.unit_id,
            consumption_unit_id=unit.unit_id,
            shelf_life_days=12,
            critical_stock_quantity="5",
        ),
        correlation_id="ingredient-tomato",
    )
    procurement = ProcurementService(store=PostgresProcurementStore(database_url))
    supplier = procurement.create_supplier(
        SupplierIdentity(identity.tenant_id, identity.actor_id, identity.role),
        CreateSupplier(name="Local Produce", code=f"produce-{uuid4().hex[:6]}"),
        correlation_id="supplier",
    )
    procurement.create_supplier_offer(
        SupplierIdentity(identity.tenant_id, identity.actor_id, identity.role),
        CreateSupplierOffer(
            supplier_id=supplier.supplier_id,
            ingredient_id=ingredient.ingredient_id,
            purchase_unit_id=unit.unit_id,
            price="3.50",
            currency="USD",
            effective_from=date.today(),
            effective_until=None,
        ),
        correlation_id="offer",
    )
    return ingredient.ingredient_id, unit.unit_id


def branch_id_for(
    postgres_connection: psycopg.Connection[tuple[object, ...]],
    tenant_id: str,
) -> str:
    return str(
        postgres_connection.execute(
            "select id from platform_branches where tenant_id = %s order by code limit 1",
            (tenant_id,),
        ).fetchone()[0]
    )


def test_menu_item_approval_records_theoretical_cost_and_branch_margin(
    postgres_connection: psycopg.Connection[tuple[object, ...]],
    database_url: str,
) -> None:
    identity = registered_admin(database_url)
    ingredient_id, unit_id = seed_ingredient_with_offer(database_url, identity)
    branch_id = branch_id_for(postgres_connection, identity.tenant_id)
    service = MenuRecipeService(store=PostgresMenuCatalogStore(database_url))
    sub_recipe = service.approve_sub_recipe_version(
        identity,
        CreateSubRecipeVersion(
            name="Tomato base",
            code="tomato-base",
            version="v1",
            yield_quantity="2",
            yield_unit_id=unit_id,
            effective_from=date.today(),
            components=(
                CreateRecipeComponent("ingredient", ingredient_id, "4", unit_id),
            ),
        ),
        correlation_id="sub-recipe",
    )

    menu_item = service.approve_menu_item_version(
        identity,
        CreateMenuItemVersion(
            name="Tomato bowl",
            code="tomato-bowl",
            version="v1",
            yield_quantity="1",
            yield_unit_id=unit_id,
            effective_from=date.today(),
            components=(
                CreateRecipeComponent("sub_recipe", sub_recipe.recipe_id, "1", unit_id),
            ),
        ),
        correlation_id="menu-item",
    )
    margin = service.create_branch_price(
        identity,
        CreateBranchMenuPrice(
            menu_item_version_id=menu_item.recipe_version_id,
            branch_id=branch_id,
            price="20",
            currency="usd",
            effective_from=date.today(),
        ),
        correlation_id="branch-price",
    )

    assert menu_item.is_active
    assert menu_item.cost_snapshot.total_cost == Decimal("7.0000000000")
    assert margin.theoretical_cost == Decimal("7.0000000000")
    assert margin.contribution_margin == Decimal("13.0000000000")
    assert margin.margin_percent == Decimal("65.0000000000")
    assert margin.suggested_price == Decimal("21.0000000000")

    with postgres_connection.transaction():
        rows = postgres_connection.execute(
            """
            select r.recipe_type, s.total_cost, p.price
            from menu_recipes r
            join menu_recipe_versions v on v.recipe_id = r.id
            join menu_cost_snapshots s on s.recipe_version_id = v.id
            join menu_item_branch_prices p on p.recipe_version_id = v.id
            where r.tenant_id = %s and v.id = %s
            """,
            (identity.tenant_id, menu_item.recipe_version_id),
        ).fetchall()

    assert rows == [("menu_item", Decimal("7.0000000000"), Decimal("20.0000000000"))]


def test_menu_item_approval_requires_current_cost_evidence(database_url: str) -> None:
    identity = registered_admin(database_url)
    catalog = MenuCatalogService(store=PostgresMenuCatalogStore(database_url))
    unit = catalog.create_unit(
        identity,
        CreateUnit(name="Each", code="each-missing", dimension="count"),
        correlation_id="unit-each",
    )
    ingredient = catalog.create_ingredient(
        identity,
        CreateIngredient(
            name="No offer ingredient",
            code="no-offer-ingredient",
            purchase_unit_id=unit.unit_id,
            consumption_unit_id=unit.unit_id,
            shelf_life_days=10,
            critical_stock_quantity="1",
        ),
        correlation_id="ingredient-no-offer",
    )
    service = MenuRecipeService(store=PostgresMenuCatalogStore(database_url))

    with pytest.raises(RecipeMissingCost):
        service.approve_menu_item_version(
            identity,
            CreateMenuItemVersion(
                name="Missing offer bowl",
                code="missing-offer-bowl",
                version="v1",
                yield_quantity="1",
                yield_unit_id=unit.unit_id,
                effective_from=date.today(),
                components=(
                    CreateRecipeComponent(
                        "ingredient",
                        ingredient.ingredient_id,
                        "1",
                        unit.unit_id,
                    ),
                ),
            ),
            correlation_id="missing-cost",
        )
