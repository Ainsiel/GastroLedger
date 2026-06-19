from datetime import date, timedelta
from decimal import Decimal
from uuid import uuid4

import psycopg
import pytest

from gastroledger_api.modules.menu_engineering.public import (
    CreateIngredient,
    CreateRecipeComponent,
    CreateSubRecipeVersion,
    CreateUnit,
    MenuCatalogService,
    MenuRecipeService,
    RecipeGraphViolation,
    RecipeVersionConflict,
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
    slug = f"recipe-{uuid4().hex}"
    result = RegisterTenant(
        store=PostgresPlatformStore(database_url),
        password_hasher=ScryptPasswordHasher(),
        session_tokens=SessionTokenIssuer(),
    ).execute(
        RegistrationCommand(
            tenant_name="Recipe Tenant",
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


def test_sub_recipe_approval_is_immutable_and_records_cost_snapshot(
    postgres_connection: psycopg.Connection[tuple[object, ...]],
    database_url: str,
) -> None:
    identity = registered_admin(database_url)
    ingredient_id, unit_id = seed_ingredient_with_offer(database_url, identity)
    service = MenuRecipeService(store=PostgresMenuCatalogStore(database_url))

    approved = service.approve_sub_recipe_version(
        identity,
        CreateSubRecipeVersion(
            name="Tomato base",
            code="tomato-base",
            version="v1",
            yield_quantity="2",
            yield_unit_id=unit_id,
            effective_from=date.today(),
            components=(
                CreateRecipeComponent(
                    component_type="ingredient",
                    component_id=ingredient_id,
                    quantity="4",
                    unit_id=unit_id,
                ),
            ),
        ),
        correlation_id="recipe-v1",
    )

    with pytest.raises(RecipeVersionConflict):
        service.approve_sub_recipe_version(
            identity,
            CreateSubRecipeVersion(
                name="Tomato base changed",
                code="tomato-base",
                version="v1",
                yield_quantity="3",
                yield_unit_id=unit_id,
                effective_from=date.today(),
                components=(
                    CreateRecipeComponent(
                        component_type="ingredient",
                        component_id=ingredient_id,
                        quantity="1",
                        unit_id=unit_id,
                    ),
                ),
            ),
            correlation_id="recipe-v1-repeat",
        )

    with postgres_connection.transaction():
        row = postgres_connection.execute(
            """
            select r.code, v.version, v.status, s.total_cost, s.status
            from menu_recipes r
            join menu_recipe_versions v on v.recipe_id = r.id
            join menu_cost_snapshots s on s.recipe_version_id = v.id
            where r.tenant_id = %s and v.id = %s
            """,
            (identity.tenant_id, approved.recipe_version_id),
        ).fetchone()

    assert approved.is_active
    assert approved.cost_snapshot.total_cost == Decimal("14.0000000000")
    assert row == (
        "TOMATO-BASE",
        "v1",
        "approved",
        Decimal("14.0000000000"),
        "current",
    )


def test_future_version_does_not_replace_active_version_early(database_url: str) -> None:
    identity = registered_admin(database_url)
    ingredient_id, unit_id = seed_ingredient_with_offer(database_url, identity)
    service = MenuRecipeService(store=PostgresMenuCatalogStore(database_url))

    current = service.approve_sub_recipe_version(
        identity,
        CreateSubRecipeVersion(
            name="Sauce base",
            code="sauce-base",
            version="v1",
            yield_quantity="1",
            yield_unit_id=unit_id,
            effective_from=date.today(),
            components=(
                CreateRecipeComponent("ingredient", ingredient_id, "1", unit_id),
            ),
        ),
        correlation_id="current",
    )
    future = service.approve_sub_recipe_version(
        identity,
        CreateSubRecipeVersion(
            name="Sauce base",
            code="sauce-base",
            version="v2",
            yield_quantity="1",
            yield_unit_id=unit_id,
            effective_from=date.today() + timedelta(days=7),
            components=(
                CreateRecipeComponent("ingredient", ingredient_id, "2", unit_id),
            ),
        ),
        correlation_id="future",
    )

    assert current.is_active
    assert future.status == "scheduled"
    assert not future.is_active


def test_recipe_graph_cycle_or_excessive_depth_is_rejected(database_url: str) -> None:
    identity = registered_admin(database_url)
    ingredient_id, unit_id = seed_ingredient_with_offer(database_url, identity)
    service = MenuRecipeService(store=PostgresMenuCatalogStore(database_url))
    child = service.approve_sub_recipe_version(
        identity,
        CreateSubRecipeVersion(
            name="Child base",
            code="child-base",
            version="v1",
            yield_quantity="1",
            yield_unit_id=unit_id,
            effective_from=date.today(),
            components=(
                CreateRecipeComponent("ingredient", ingredient_id, "1", unit_id),
            ),
        ),
        correlation_id="child",
    )

    with pytest.raises(RecipeGraphViolation):
        service.approve_sub_recipe_version(
            identity,
            CreateSubRecipeVersion(
                name="Parent base",
                code="parent-base",
                version="v1",
                yield_quantity="1",
                yield_unit_id=unit_id,
                effective_from=date.today(),
                components=(
                    CreateRecipeComponent("sub_recipe", child.recipe_id, "1", unit_id),
                ),
            ),
            correlation_id="parent",
        )
