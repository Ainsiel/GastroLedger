import json
from datetime import date, timedelta
from typing import Any
from urllib.error import HTTPError
from urllib.request import Request, urlopen
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
from gastroledger_api.modules.platform_organization.public import OperatingIdentity
from gastroledger_api.modules.procurement.public import (
    CreateSupplier,
    CreateSupplierOffer,
    ProcurementDateOverlap,
    ProcurementService,
)
from gastroledger_api.technical.postgres_menu import PostgresMenuCatalogStore
from gastroledger_api.technical.postgres_platform import PostgresPlatformStore
from gastroledger_api.technical.postgres_procurement import PostgresProcurementStore


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
    slug = f"procurement-{uuid4().hex}"
    result = RegisterTenant(
        store=PostgresPlatformStore(database_url),
        password_hasher=ScryptPasswordHasher(),
        session_tokens=SessionTokenIssuer(),
    ).execute(
        RegistrationCommand(
            tenant_name="Procurement Tenant",
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


def seed_catalog(database_url: str, identity: OperatingIdentity) -> tuple[str, str]:
    service = MenuCatalogService(store=PostgresMenuCatalogStore(database_url))
    unit = service.create_unit(
        identity,
        CreateUnit(name="Each", code=f"EA-{uuid4().hex[:8]}", dimension="count"),
        correlation_id="unit-each",
    )
    ingredient = service.create_ingredient(
        identity,
        CreateIngredient(
            name="Egg",
            code=f"EGG-{uuid4().hex[:8]}",
            purchase_unit_id=unit.unit_id,
            consumption_unit_id=unit.unit_id,
            shelf_life_days=21,
            critical_stock_quantity="30",
        ),
        correlation_id="ingredient-egg",
    )
    return unit.unit_id, ingredient.ingredient_id


def test_supplier_offer_history_and_overlap_are_tenant_scoped(
    postgres_connection: psycopg.Connection[tuple[object, ...]],
    database_url: str,
) -> None:
    identity = registered_admin(database_url)
    other = registered_admin(database_url)
    unit_id, ingredient_id = seed_catalog(database_url, identity)
    store = PostgresProcurementStore(database_url)
    service = ProcurementService(store=store)

    supplier = service.create_supplier(
        identity,
        CreateSupplier(name="North Market", code="north"),
        correlation_id="supplier-create",
    )
    first = service.create_supplier_offer(
        identity,
        CreateSupplierOffer(
            supplier_id=supplier.supplier_id,
            ingredient_id=ingredient_id,
            purchase_unit_id=unit_id,
            price="12.50",
            currency="USD",
            effective_from=date.today(),
            effective_until=date.today() + timedelta(days=10),
        ),
        correlation_id="offer-current",
    )
    future = service.create_supplier_offer(
        identity,
        CreateSupplierOffer(
            supplier_id=supplier.supplier_id,
            ingredient_id=ingredient_id,
            purchase_unit_id=unit_id,
            price="13.50",
            currency="USD",
            effective_from=date.today() + timedelta(days=11),
            effective_until=None,
        ),
        correlation_id="offer-future",
    )

    with pytest.raises(ProcurementDateOverlap):
        service.create_supplier_offer(
            identity,
            CreateSupplierOffer(
                supplier_id=supplier.supplier_id,
                ingredient_id=ingredient_id,
                purchase_unit_id=unit_id,
                price="14.50",
                currency="USD",
                effective_from=date.today() + timedelta(days=5),
                effective_until=None,
            ),
            correlation_id="offer-overlap",
        )

    with postgres_connection.transaction():
        audit_actions = postgres_connection.execute(
            """
            select action, correlation_id
            from control_audit_events
            where tenant_id = %s and action like 'procurement.%%'
            order by occurred_at
            """,
            (identity.tenant_id,),
        ).fetchall()

    assert first.price == future.price - 1
    assert service.list_suppliers(identity)[0].code == "NORTH"
    assert service.list_suppliers(other) == ()
    assert audit_actions == [
        ("procurement.supplier.created", "supplier-create"),
        ("procurement.offer.created", "offer-current"),
        ("procurement.offer.created", "offer-future"),
    ]


def test_http_supplier_offer_flow_is_session_scoped(api_base_url: str) -> None:
    slug = f"http-procurement-{uuid4().hex}"
    created_status, _created, created_headers = http_json(
        "POST",
        f"{api_base_url}/api/v1/tenants/register",
        payload={
            "tenantName": "HTTP Procurement Tenant",
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

    supplier_status, supplier, _ = http_json(
        "POST",
        f"{api_base_url}/api/v1/procurement/suppliers",
        payload={"name": "North Market", "code": "north"},
        cookie=cookie,
    )
    offer_status, offer, _ = http_json(
        "POST",
        f"{api_base_url}/api/v1/procurement/offers",
        payload={
            "supplierId": supplier["supplierId"],
            "ingredientId": ingredient["ingredientId"],
            "purchaseUnitId": unit["unitId"],
            "price": "12.50",
            "currency": "USD",
            "effectiveFrom": str(date.today()),
            "effectiveUntil": None,
        },
        cookie=cookie,
    )
    list_status, offers, _ = http_json(
        "GET", f"{api_base_url}/api/v1/procurement/offers", cookie=cookie
    )
    unauthorized_status, unauthorized, _ = http_json(
        "GET", f"{api_base_url}/api/v1/procurement/suppliers"
    )

    assert created_status == 201
    assert unit_status == 201
    assert ingredient_status == 201
    assert supplier_status == 201
    assert supplier["code"] == "NORTH"
    assert offer_status == 201
    assert offer["price"] == "12.5"
    assert list_status == 200
    assert offers[0]["supplierId"] == supplier["supplierId"]
    assert unauthorized_status == 401
    assert unauthorized["type"] == "procurement.authentication_required"
