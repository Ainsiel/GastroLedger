import json
from datetime import date, timedelta
from decimal import Decimal
from typing import Any
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from uuid import uuid4

import psycopg
import pytest

from gastroledger_api.modules.menu_engineering.public import (
    ArchiveIngredient,
    CreateConversionFactor,
    CreateIngredient,
    CreateUnit,
    IngredientArchived,
    MenuCatalogService,
    UnitConversionUnavailable,
    UnitDimensionMismatch,
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
from gastroledger_api.technical.postgres_menu import PostgresMenuCatalogStore
from gastroledger_api.technical.postgres_platform import PostgresPlatformStore


def http_json(
    method: str,
    url: str,
    *,
    payload: dict[str, object] | None = None,
    cookie: str | None = None,
) -> tuple[int, Any, Any]:
    headers = {"content-type": "application/json"}
    if cookie:
        headers["cookie"] = cookie
    request = Request(
        url,
        method=method,
        headers=headers,
        data=json.dumps(payload).encode() if payload is not None else None,
    )
    try:
        with urlopen(request, timeout=5) as response:
            return response.status, json.loads(response.read()), response.headers
    except HTTPError as error:
        return error.code, json.loads(error.read()), error.headers


def registered_admin(database_url: str) -> OperatingIdentity:
    slug = f"menu-{uuid4().hex}"
    result = RegisterTenant(
        store=PostgresPlatformStore(database_url),
        password_hasher=ScryptPasswordHasher(),
        session_tokens=SessionTokenIssuer(),
    ).execute(
        RegistrationCommand(
            tenant_name="Menu Tenant",
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


def test_effective_dated_conversion_and_archived_ingredient_history(
    postgres_connection: psycopg.Connection[tuple[object, ...]],
    database_url: str,
) -> None:
    identity = registered_admin(database_url)
    service = MenuCatalogService(store=PostgresMenuCatalogStore(database_url))

    kilogram = service.create_unit(
        identity,
        CreateUnit(name="Kilogram", code="kg", dimension="mass"),
        correlation_id="unit-kg",
    )
    gram = service.create_unit(
        identity,
        CreateUnit(name="Gram", code="g", dimension="mass"),
        correlation_id="unit-g",
    )
    liter = service.create_unit(
        identity,
        CreateUnit(name="Liter", code="l", dimension="volume"),
        correlation_id="unit-l",
    )

    today = date.today()
    service.create_conversion_factor(
        identity,
        CreateConversionFactor(
            source_unit_id=kilogram.unit_id,
            target_unit_id=gram.unit_id,
            factor="1000",
            effective_from=today,
        ),
        correlation_id="factor-current",
    )
    service.create_conversion_factor(
        identity,
        CreateConversionFactor(
            source_unit_id=kilogram.unit_id,
            target_unit_id=gram.unit_id,
            factor="990",
            effective_from=today + timedelta(days=1),
        ),
        correlation_id="factor-future",
    )

    converted_today = service.convert_quantity(
        identity,
        source_unit_id=kilogram.unit_id,
        target_unit_id=gram.unit_id,
        quantity=Decimal("1.25"),
        as_of=today,
    )
    converted_future = service.convert_quantity(
        identity,
        source_unit_id=kilogram.unit_id,
        target_unit_id=gram.unit_id,
        quantity=Decimal("1.25"),
        as_of=today + timedelta(days=1),
    )

    with pytest.raises(UnitDimensionMismatch):
        service.create_conversion_factor(
            identity,
            CreateConversionFactor(
                source_unit_id=kilogram.unit_id,
                target_unit_id=liter.unit_id,
                factor="1",
                effective_from=today,
            ),
            correlation_id="factor-mismatch",
        )

    ingredient = service.create_ingredient(
        identity,
        CreateIngredient(
            name="Flour",
            code="flour",
            purchase_unit_id=kilogram.unit_id,
            consumption_unit_id=gram.unit_id,
            shelf_life_days=180,
            critical_stock_quantity="12.5",
        ),
        correlation_id="ingredient-flour",
    )
    archived = service.archive_ingredient(
        identity,
        ArchiveIngredient(ingredient_id=ingredient.ingredient_id),
        correlation_id="ingredient-archive",
    )
    with pytest.raises(IngredientArchived):
        service.archive_ingredient(
            identity,
            ArchiveIngredient(ingredient_id=ingredient.ingredient_id),
            correlation_id="ingredient-archive-again",
        )

    with postgres_connection.transaction():
        ingredient_row = postgres_connection.execute(
            """
            select code, status, critical_stock_quantity
            from menu_ingredients
            where tenant_id = %s and id = %s
            """,
            (identity.tenant_id, ingredient.ingredient_id),
        ).fetchone()
        audit_actions = postgres_connection.execute(
            """
            select action, correlation_id
            from control_audit_events
            where tenant_id = %s and action like 'menu.%%'
            order by occurred_at
            """,
            (identity.tenant_id,),
        ).fetchall()

    assert converted_today.quantity == Decimal("1250.0000000000")
    assert converted_future.quantity == Decimal("1237.5000000000")
    assert archived.status == "archived"
    assert not archived.available_for_new_use
    assert ingredient_row == ("FLOUR", "archived", Decimal("12.5000000000"))
    assert audit_actions == [
        ("menu.unit.created", "unit-kg"),
        ("menu.unit.created", "unit-g"),
        ("menu.unit.created", "unit-l"),
        ("menu.conversion_factor.created", "factor-current"),
        ("menu.conversion_factor.created", "factor-future"),
        ("menu.ingredient.created", "ingredient-flour"),
        ("menu.ingredient.archived", "ingredient-archive"),
    ]


def test_missing_conversion_and_cross_tenant_visibility_are_blocked(
    database_url: str,
) -> None:
    owner = registered_admin(database_url)
    attacker = registered_admin(database_url)
    service = MenuCatalogService(store=PostgresMenuCatalogStore(database_url))
    kilogram = service.create_unit(
        owner,
        CreateUnit(name="Kilogram", code="kg", dimension="mass"),
        correlation_id="unit-kg",
    )
    gram = service.create_unit(
        owner,
        CreateUnit(name="Gram", code="g", dimension="mass"),
        correlation_id="unit-g",
    )

    with pytest.raises(UnitConversionUnavailable):
        service.create_ingredient(
            owner,
            CreateIngredient(
                name="Flour",
                code="flour",
                purchase_unit_id=kilogram.unit_id,
                consumption_unit_id=gram.unit_id,
                shelf_life_days=180,
                critical_stock_quantity="12.5",
            ),
            correlation_id="ingredient-flour",
        )

    with psycopg.connect(database_url) as runtime_connection:
        with runtime_connection.transaction():
            runtime_connection.execute("set local role gastroledger_app")
            runtime_connection.execute(
                "select set_config('app.current_tenant_id', %s, true)",
                (attacker.tenant_id,),
            )
            hidden_units = runtime_connection.execute(
                "select id from menu_units where tenant_id = %s",
                (owner.tenant_id,),
            ).fetchall()
            changed_units = runtime_connection.execute(
                """
                update menu_units
                set name = 'Cross Tenant'
                where tenant_id = %s
                returning id
                """,
                (owner.tenant_id,),
            ).fetchall()

    assert hidden_units == []
    assert changed_units == []


def test_http_menu_catalog_flow_is_session_scoped(
    api_base_url: str,
) -> None:
    slug = f"http-menu-{uuid4().hex}"
    created_status, _created, created_headers = http_json(
        "POST",
        f"{api_base_url}/api/v1/tenants/register",
        payload={
            "tenantName": "HTTP Menu Tenant",
            "tenantSlug": slug,
            "adminEmail": f"{slug}@example.com",
            "password": "StrongPassword123",
        },
    )
    cookie = created_headers["set-cookie"].split(";", 1)[0]

    unit_status, unit, _ = http_json(
        "POST",
        f"{api_base_url}/api/v1/menu/units",
        payload={"name": "Each", "code": "ea", "dimension": "count"},
        cookie=cookie,
    )
    ingredient_status, ingredient, _ = http_json(
        "POST",
        f"{api_base_url}/api/v1/menu/ingredients",
        payload={
            "name": "Egg",
            "code": "egg",
            "purchaseUnitId": unit["unitId"],
            "consumptionUnitId": unit["unitId"],
            "shelfLifeDays": 21,
            "criticalStockQuantity": "30",
        },
        cookie=cookie,
    )
    list_status, ingredients, _ = http_json(
        "GET", f"{api_base_url}/api/v1/menu/ingredients", cookie=cookie
    )
    unauthorized_status, unauthorized, _ = http_json(
        "GET", f"{api_base_url}/api/v1/menu/units"
    )

    assert created_status == 201
    assert unit_status == 201
    assert unit["code"] == "EA"
    assert ingredient_status == 201
    assert ingredient["availableForNewUse"]
    assert list_status == 200
    assert ingredients[0]["code"] == "EGG"
    assert unauthorized_status == 401
    assert unauthorized["type"] == "menu.authentication_required"
