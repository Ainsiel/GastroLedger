import json
from typing import Any
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from uuid import uuid4

import psycopg
import pytest

from gastroledger_api.modules.platform_organization.application.registration import (
    RegisterTenant,
    RegistrationCommand,
)
from gastroledger_api.modules.platform_organization.application.security import (
    ScryptPasswordHasher,
    SessionTokenIssuer,
)
from gastroledger_api.modules.platform_organization.public import (
    BranchLimitExceeded,
    CreateBranch,
    CreateWarehouse,
    DeactivateWarehouse,
    OperatingAuthorizationDenied,
    OperatingCodeConflict,
    OperatingIdentity,
    OperatingScopeService,
    UpdateTenantSettings,
    WarehouseInactive,
)
from gastroledger_api.technical.postgres_platform import PostgresPlatformStore


class NoOpenMovements:
    def has_open_movements(self, _identity: object, _warehouse_id: object) -> bool:
        return False


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


def registered_admin(database_url: str) -> tuple[PostgresPlatformStore, OperatingIdentity]:
    store = PostgresPlatformStore(database_url)
    slug = f"operating-{uuid4().hex}"
    result = RegisterTenant(
        store=store,
        password_hasher=ScryptPasswordHasher(),
        session_tokens=SessionTokenIssuer(),
    ).execute(
        RegistrationCommand(
            tenant_name="Operating Tenant",
            tenant_slug=slug,
            admin_email=f"{slug}@example.com",
            password="StrongPassword123",
            branch_name="Main",
            branch_code="MAIN",
        )
    )
    return store, OperatingIdentity(
        tenant_id=result.tenant_id,
        actor_id=result.actor_id,
        role="tenant_admin",
    )


def test_settings_limit_reduction_preserves_branches_and_blocks_the_next_creation(
    postgres_connection: psycopg.Connection[tuple[object, ...]],
    database_url: str,
) -> None:
    store, identity = registered_admin(database_url)
    service = OperatingScopeService(store=store, movement_guard=NoOpenMovements())

    service.update_settings(
        identity,
        UpdateTenantSettings(locale="es", base_currency="CLP", branch_limit=2),
        correlation_id="settings-expand",
    )
    service.create_branch(
        identity,
        CreateBranch(name="Second", code="SECOND"),
        correlation_id="branch-second",
    )
    service.update_settings(
        identity,
        UpdateTenantSettings(locale="es", base_currency="CLP", branch_limit=1),
        correlation_id="settings-reduce",
    )

    with pytest.raises(BranchLimitExceeded):
        service.create_branch(
            identity,
            CreateBranch(name="Third", code="THIRD"),
            correlation_id="branch-third",
        )

    with postgres_connection.transaction():
        settings = postgres_connection.execute(
            """
            select locale, base_currency, branch_limit
            from platform_tenant_settings
            where tenant_id = %s
            """,
            (identity.tenant_id,),
        ).fetchone()
        branch_count = postgres_connection.execute(
            "select count(*) from platform_branches where tenant_id = %s",
            (identity.tenant_id,),
        ).fetchone()
        audit = postgres_connection.execute(
            """
            select action, correlation_id
            from control_audit_events
            where tenant_id = %s and action = 'tenant.settings_updated'
            order by occurred_at
            """,
            (identity.tenant_id,),
        ).fetchall()

    assert settings == ("es", "CLP", 1)
    assert branch_count == (2,)
    assert audit == [
        ("tenant.settings_updated", "settings-expand"),
        ("tenant.settings_updated", "settings-reduce"),
    ]


def test_warehouse_codes_are_branch_scoped_and_safe_deactivation_retains_history(
    postgres_connection: psycopg.Connection[tuple[object, ...]],
    database_url: str,
) -> None:
    store, identity = registered_admin(database_url)
    service = OperatingScopeService(store=store, movement_guard=NoOpenMovements())
    with postgres_connection.transaction():
        branch_id = postgres_connection.execute(
            "select id from platform_branches where tenant_id = %s",
            (identity.tenant_id,),
        ).fetchone()[0]

    kitchen = service.create_warehouse(
        identity,
        CreateWarehouse(
            branch_id=str(branch_id),
            name="Kitchen",
            code="MAIN",
            warehouse_type="kitchen",
        ),
        correlation_id="warehouse-kitchen",
    )
    service.create_warehouse(
        identity,
        CreateWarehouse(
            branch_id=str(branch_id),
            name="Bar",
            code="BAR",
            warehouse_type="bar",
        ),
        correlation_id="warehouse-bar",
    )
    service.create_warehouse(
        identity,
        CreateWarehouse(
            branch_id=str(branch_id),
            name="General",
            code="GENERAL",
            warehouse_type="general",
        ),
        correlation_id="warehouse-general",
    )

    with pytest.raises(OperatingCodeConflict):
        service.create_warehouse(
            identity,
            CreateWarehouse(
                branch_id=str(branch_id),
                name="Duplicate",
                code="main",
                warehouse_type="general",
            ),
            correlation_id="warehouse-duplicate",
        )

    deactivated = service.deactivate_warehouse(
        identity,
        DeactivateWarehouse(warehouse_id=kitchen.warehouse_id),
        correlation_id="warehouse-deactivate",
    )
    with pytest.raises(WarehouseInactive):
        service.deactivate_warehouse(
            identity,
            DeactivateWarehouse(warehouse_id=kitchen.warehouse_id),
            correlation_id="warehouse-deactivate-again",
        )

    with postgres_connection.transaction():
        warehouses = postgres_connection.execute(
            """
            select code, type, status
            from platform_warehouses
            where branch_id = %s
            order by code
            """,
            (branch_id,),
        ).fetchall()

    other_store, other_identity = registered_admin(database_url)
    del other_store
    with psycopg.connect(database_url) as runtime_connection:
        with runtime_connection.transaction():
            runtime_connection.execute("set local role gastroledger_app")
            runtime_connection.execute(
                "select set_config('app.current_tenant_id', %s, true)",
                (other_identity.tenant_id,),
            )
            hidden = runtime_connection.execute(
                "select id from platform_warehouses where id = %s",
                (kitchen.warehouse_id,),
            ).fetchone()

    assert deactivated.status == "inactive"
    assert warehouses == [
        ("BAR", "bar", "active"),
        ("GENERAL", "general", "active"),
        ("MAIN", "kitchen", "inactive"),
    ]
    assert hidden is None


def test_http_tenant_admin_configures_branches_and_deactivates_warehouse(
    postgres_connection: psycopg.Connection[tuple[object, ...]],
    api_base_url: str,
) -> None:
    slug = f"http-operating-{uuid4().hex}"
    created_status, created, created_headers = http_json(
        "POST",
        f"{api_base_url}/api/v1/tenants/register",
        payload={
            "tenantName": "HTTP Operating Tenant",
            "tenantSlug": slug,
            "adminEmail": f"{slug}@example.com",
            "password": "StrongPassword123",
        },
    )
    cookie = created_headers["set-cookie"].split(";", 1)[0]

    settings_status, settings, _ = http_json(
        "PATCH",
        f"{api_base_url}/api/v1/tenant/settings",
        payload={"locale": "es", "baseCurrency": "CLP", "branchLimit": 2},
        cookie=cookie,
    )
    branch_status, branch, _ = http_json(
        "POST",
        f"{api_base_url}/api/v1/branches",
        payload={"name": "Downtown", "code": "main"},
        cookie=cookie,
    )
    warehouse_status, warehouse, _ = http_json(
        "POST",
        f"{api_base_url}/api/v1/branches/{branch['branchId']}/warehouses",
        payload={"name": "Kitchen", "code": "kitchen", "type": "kitchen"},
        cookie=cookie,
    )
    list_status, branches, _ = http_json(
        "GET", f"{api_base_url}/api/v1/branches", cookie=cookie
    )
    deactivate_status, deactivated, _ = http_json(
        "POST",
        f"{api_base_url}/api/v1/warehouses/{warehouse['warehouseId']}/deactivate",
        cookie=cookie,
    )
    unauthorized_status, unauthorized, _ = http_json(
        "GET", f"{api_base_url}/api/v1/tenant/settings"
    )
    with postgres_connection.transaction():
        audit_actions = postgres_connection.execute(
            """
            select action
            from control_audit_events
            where tenant_id = %s
            order by occurred_at
            """,
            (created["tenantId"],),
        ).fetchall()

    assert created_status == 201
    assert created["tenantSlug"] == slug
    assert settings_status == 200
    assert settings == {
        "locale": "es",
        "baseCurrency": "CLP",
        "branchLimit": 2,
        "branchCount": 0,
    }
    assert branch_status == 201
    assert branch["code"] == "MAIN"
    assert warehouse_status == 201
    assert list_status == 200
    assert branches[0]["warehouses"][0]["status"] == "active"
    assert deactivate_status == 200
    assert deactivated["status"] == "inactive"
    assert unauthorized_status == 401
    assert unauthorized["type"] == "platform.authentication_required"
    assert audit_actions == [
        ("tenant.settings_updated",),
        ("branch.created",),
        ("warehouse.created",),
        ("warehouse.deactivated",),
    ]


def test_http_unsupported_settings_and_non_admin_change_nothing(
    postgres_connection: psycopg.Connection[tuple[object, ...]],
    api_base_url: str,
) -> None:
    slug = f"http-forbidden-{uuid4().hex}"
    created_status, created, created_headers = http_json(
        "POST",
        f"{api_base_url}/api/v1/tenants/register",
        payload={
            "tenantName": "Forbidden Operating Tenant",
            "tenantSlug": slug,
            "adminEmail": f"{slug}@example.com",
            "password": "StrongPassword123",
        },
    )
    cookie = created_headers["set-cookie"].split(";", 1)[0]

    invalid_status, invalid, _ = http_json(
        "PATCH",
        f"{api_base_url}/api/v1/tenant/settings",
        payload={"locale": "es", "baseCurrency": "BTC", "branchLimit": 2},
        cookie=cookie,
    )
    with postgres_connection.transaction():
        postgres_connection.execute(
            """
            update platform_memberships
            set role = 'operator'
            where tenant_id = %s and user_id = %s
            """,
            (created["tenantId"], created["actorId"]),
        )
    forbidden_status, forbidden, _ = http_json(
        "PATCH",
        f"{api_base_url}/api/v1/tenant/settings",
        payload={"locale": "es", "baseCurrency": "CLP", "branchLimit": 2},
        cookie=cookie,
    )
    with postgres_connection.transaction():
        settings = postgres_connection.execute(
            """
            select locale, base_currency, branch_limit
            from platform_tenant_settings
            where tenant_id = %s
            """,
            (created["tenantId"],),
        ).fetchone()
        audit_count = postgres_connection.execute(
            "select count(*) from control_audit_events where tenant_id = %s",
            (created["tenantId"],),
        ).fetchone()

    assert created_status == 201
    assert invalid_status == 422
    assert invalid["type"] == "platform.operating_scope_invalid"
    assert forbidden_status == 403
    assert forbidden["type"] == "platform.authorization_denied"
    assert settings == ("en", "USD", 1)
    assert audit_count == (0,)


def test_cross_tenant_reads_and_mutations_are_blocked_at_every_boundary(
    postgres_connection: psycopg.Connection[tuple[object, ...]],
    database_url: str,
    api_base_url: str,
) -> None:
    owner_slug = f"http-owner-{uuid4().hex}"
    _, owner, owner_headers = http_json(
        "POST",
        f"{api_base_url}/api/v1/tenants/register",
        payload={
            "tenantName": "Owner Tenant",
            "tenantSlug": owner_slug,
            "adminEmail": f"{owner_slug}@example.com",
            "password": "StrongPassword123",
        },
    )
    owner_cookie = owner_headers["set-cookie"].split(";", 1)[0]
    _, owner_branch, _ = http_json(
        "POST",
        f"{api_base_url}/api/v1/branches",
        payload={"name": "Owner Branch", "code": "OWNER"},
        cookie=owner_cookie,
    )
    _, owner_warehouse, _ = http_json(
        "POST",
        f"{api_base_url}/api/v1/branches/{owner_branch['branchId']}/warehouses",
        payload={"name": "Owner Kitchen", "code": "KITCHEN", "type": "kitchen"},
        cookie=owner_cookie,
    )

    attacker_slug = f"http-attacker-{uuid4().hex}"
    _, attacker, attacker_headers = http_json(
        "POST",
        f"{api_base_url}/api/v1/tenants/register",
        payload={
            "tenantName": "Attacker Tenant",
            "tenantSlug": attacker_slug,
            "adminEmail": f"{attacker_slug}@example.com",
            "password": "StrongPassword123",
        },
    )
    attacker_cookie = attacker_headers["set-cookie"].split(";", 1)[0]

    forged_identity = OperatingIdentity(
        tenant_id=owner["tenantId"],
        actor_id=attacker["actorId"],
        role="tenant_admin",
    )
    service = OperatingScopeService(
        store=PostgresPlatformStore(database_url),
        movement_guard=NoOpenMovements(),
    )
    with pytest.raises(OperatingAuthorizationDenied):
        service.get_settings(forged_identity)
    with pytest.raises(OperatingAuthorizationDenied):
        service.list_branches(forged_identity)
    with pytest.raises(OperatingAuthorizationDenied):
        service.update_settings(
            forged_identity,
            UpdateTenantSettings(locale="es", base_currency="CLP", branch_limit=2),
            correlation_id="forged-settings",
        )
    with pytest.raises(OperatingAuthorizationDenied):
        service.create_branch(
            forged_identity,
            CreateBranch(name="Forged Branch", code="FORGED"),
            correlation_id="forged-branch",
        )
    with pytest.raises(OperatingAuthorizationDenied):
        service.create_warehouse(
            forged_identity,
            CreateWarehouse(
                branch_id=owner_branch["branchId"],
                name="Forged Warehouse",
                code="FORGED",
                warehouse_type="general",
            ),
            correlation_id="forged-warehouse",
        )
    with pytest.raises(OperatingAuthorizationDenied):
        service.deactivate_warehouse(
            forged_identity,
            DeactivateWarehouse(warehouse_id=owner_warehouse["warehouseId"]),
            correlation_id="forged-deactivation",
        )

    settings_status, attacker_settings, _ = http_json(
        "GET", f"{api_base_url}/api/v1/tenant/settings", cookie=attacker_cookie
    )
    branches_status, attacker_branches, _ = http_json(
        "GET", f"{api_base_url}/api/v1/branches", cookie=attacker_cookie
    )
    create_status, create_problem, _ = http_json(
        "POST",
        f"{api_base_url}/api/v1/branches/{owner_branch['branchId']}/warehouses",
        payload={"name": "HTTP Forged", "code": "FORGED", "type": "general"},
        cookie=attacker_cookie,
    )
    deactivate_status, deactivate_problem, _ = http_json(
        "POST",
        f"{api_base_url}/api/v1/warehouses/{owner_warehouse['warehouseId']}/deactivate",
        cookie=attacker_cookie,
    )
    patch_status, patched_attacker_settings, _ = http_json(
        "PATCH",
        f"{api_base_url}/api/v1/tenant/settings",
        payload={"locale": "es", "baseCurrency": "CLP", "branchLimit": 2},
        cookie=attacker_cookie,
    )

    with psycopg.connect(database_url) as runtime_connection:
        with runtime_connection.transaction():
            runtime_connection.execute("set local role gastroledger_app")
            runtime_connection.execute(
                "select set_config('app.current_tenant_id', %s, true)",
                (attacker["tenantId"],),
            )
            hidden_settings = runtime_connection.execute(
                "select tenant_id from platform_tenant_settings where tenant_id = %s",
                (owner["tenantId"],),
            ).fetchone()
            hidden_branches = runtime_connection.execute(
                "select id from platform_branches where tenant_id = %s",
                (owner["tenantId"],),
            ).fetchall()
            hidden_warehouses = runtime_connection.execute(
                "select id from platform_warehouses where tenant_id = %s",
                (owner["tenantId"],),
            ).fetchall()
            changed_settings = runtime_connection.execute(
                """
                update platform_tenant_settings
                set locale = 'pt-br'
                where tenant_id = %s
                returning tenant_id
                """,
                (owner["tenantId"],),
            ).fetchall()
            changed_warehouses = runtime_connection.execute(
                """
                update platform_warehouses
                set status = 'inactive'
                where tenant_id = %s
                returning id
                """,
                (owner["tenantId"],),
            ).fetchall()

    with (
        pytest.raises(psycopg.errors.InsufficientPrivilege),
        psycopg.connect(database_url) as branch_mutation_connection,
        branch_mutation_connection.transaction(),
    ):
        branch_mutation_connection.execute("set local role gastroledger_app")
        branch_mutation_connection.execute(
            "select set_config('app.current_tenant_id', %s, true)",
            (attacker["tenantId"],),
        )
        branch_mutation_connection.execute(
            """
            insert into platform_branches (id, tenant_id, code, name)
            values (%s, %s, 'CROSS', 'Cross tenant branch')
            """,
            (str(uuid4()), owner["tenantId"]),
        )

    with postgres_connection.transaction():
        owner_settings = postgres_connection.execute(
            """
            select locale, base_currency, branch_limit
            from platform_tenant_settings
            where tenant_id = %s
            """,
            (owner["tenantId"],),
        ).fetchone()
        owner_branch_name = postgres_connection.execute(
            "select name from platform_branches where id = %s",
            (owner_branch["branchId"],),
        ).fetchone()
        owner_warehouse_status = postgres_connection.execute(
            "select status from platform_warehouses where id = %s",
            (owner_warehouse["warehouseId"],),
        ).fetchone()

    assert settings_status == 200
    assert attacker_settings["locale"] == "en"
    assert branches_status == 200
    assert all(branch["branchId"] != owner_branch["branchId"] for branch in attacker_branches)
    assert create_status == 404
    assert create_problem["type"] == "platform.operating_scope_not_found"
    assert deactivate_status == 404
    assert deactivate_problem["type"] == "platform.operating_scope_not_found"
    assert patch_status == 200
    assert patched_attacker_settings["locale"] == "es"
    assert hidden_settings is None
    assert hidden_branches == []
    assert hidden_warehouses == []
    assert changed_settings == []
    assert changed_warehouses == []
    assert owner_settings == ("en", "USD", 1)
    assert owner_branch_name == ("Owner Branch",)
    assert owner_warehouse_status == ("active",)
