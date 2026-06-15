import json
from concurrent.futures import ThreadPoolExecutor
from typing import Any
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from uuid import uuid4

import psycopg
import pytest

from gastroledger_api.modules.platform_organization.application.registration import (
    RegisterTenant,
    RegistrationCommand,
    RegistrationConflict,
)
from gastroledger_api.modules.platform_organization.application.security import (
    ScryptPasswordHasher,
    SessionTokenIssuer,
)
from gastroledger_api.modules.platform_organization.domain.registration import (
    RegistrationValidationError,
)
from gastroledger_api.technical.postgres_platform import PostgresPlatformStore


def command(slug: str, *, with_branch: bool = False) -> RegistrationCommand:
    return RegistrationCommand(
        tenant_name=f"Tenant {slug}",
        tenant_slug=slug,
        admin_email=f"admin-{slug}@example.com",
        password="StrongPassword123",
        branch_name="Downtown" if with_branch else None,
        branch_code="MAIN" if with_branch else None,
    )


def register(database_url: str, registration: RegistrationCommand):
    return RegisterTenant(
        store=PostgresPlatformStore(database_url),
        password_hasher=ScryptPasswordHasher(),
        session_tokens=SessionTokenIssuer(),
    ).execute(registration)


def http_json(
    method: str,
    url: str,
    *,
    payload: dict[str, object] | None = None,
    cookie: str | None = None,
) -> tuple[int, dict[str, Any], Any]:
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


def registration_payload(slug: str) -> dict[str, object]:
    return {
        "tenantName": f"Tenant {slug}",
        "tenantSlug": slug,
        "adminEmail": f"admin-{slug}@example.com",
        "password": "StrongPassword123",
    }


def test_registration_atomically_creates_tenant_admin_session_and_optional_branch(
    postgres_connection: psycopg.Connection[tuple[object, ...]],
    database_url: str,
) -> None:
    slug = f"tenant-{uuid4().hex}"

    result = register(database_url, command(slug, with_branch=True))

    with postgres_connection.transaction():
        tenant = postgres_connection.execute(
            "select slug from platform_tenants where id = %s", (result.tenant_id,)
        ).fetchone()
        membership = postgres_connection.execute(
            """
            select role
            from platform_memberships
            where tenant_id = %s and user_id = %s
            """,
            (result.tenant_id, result.actor_id),
        ).fetchone()
        branch = postgres_connection.execute(
            "select code from platform_branches where id = %s", (result.branch_id,)
        ).fetchone()
        session = postgres_connection.execute(
            "select token_hash from platform_sessions where tenant_id = %s",
            (result.tenant_id,),
        ).fetchone()

    assert tenant == (slug,)
    assert membership == ("tenant_admin",)
    assert branch == ("MAIN",)
    assert session is not None
    assert result.session_token not in session[0]


def test_concurrent_duplicate_slug_commits_exactly_one_registration(
    postgres_connection: psycopg.Connection[tuple[object, ...]],
    database_url: str,
) -> None:
    slug = f"same-{uuid4().hex}"

    def attempt() -> str:
        try:
            register(database_url, command(slug))
            return "created"
        except RegistrationConflict:
            return "conflict"

    with ThreadPoolExecutor(max_workers=2) as pool:
        outcomes = list(pool.map(lambda _: attempt(), range(2)))

    with postgres_connection.transaction():
        count = postgres_connection.execute(
            "select count(*) from platform_tenants where slug = %s", (slug,)
        ).fetchone()

    assert sorted(outcomes) == ["conflict", "created"]
    assert count == (1,)


def test_invalid_credentials_leave_no_partial_tenant(
    postgres_connection: psycopg.Connection[tuple[object, ...]],
    database_url: str,
) -> None:
    slug = f"invalid-{uuid4().hex}"
    invalid = command(slug)
    invalid = RegistrationCommand(
        tenant_name=invalid.tenant_name,
        tenant_slug=invalid.tenant_slug,
        admin_email=invalid.admin_email,
        password="weak",
    )

    try:
        register(database_url, invalid)
    except RegistrationValidationError:
        pass
    else:
        raise AssertionError("invalid credentials must reject registration")

    with postgres_connection.transaction():
        count = postgres_connection.execute(
            "select count(*) from platform_tenants where slug = %s", (slug,)
        ).fetchone()

    assert count == (0,)


def test_http_session_scope_hides_another_tenant_and_records_denial_audit(
    postgres_connection: psycopg.Connection[tuple[object, ...]],
    api_base_url: str,
) -> None:
    first_slug = f"first-{uuid4().hex}"
    second_slug = f"second-{uuid4().hex}"
    first_status, first, first_headers = http_json(
        "POST",
        f"{api_base_url}/api/v1/tenants/register",
        payload=registration_payload(first_slug),
    )
    second_status, second, _second_headers = http_json(
        "POST",
        f"{api_base_url}/api/v1/tenants/register",
        payload=registration_payload(second_slug),
    )
    cookie = first_headers["set-cookie"].split(";", 1)[0]

    hidden_status, hidden, _hidden_headers = http_json(
        "GET",
        f"{api_base_url}/api/v1/session/tenant?tenantId={second['tenantId']}",
        cookie=cookie,
    )

    with postgres_connection.transaction():
        audit = postgres_connection.execute(
            """
            select action, object_reference, correlation_id
            from control_audit_events
            where tenant_id = %s
            order by occurred_at desc
            limit 1
            """,
            (first["tenantId"],),
        ).fetchone()

    assert first_status == 201
    assert second_status == 201
    assert hidden_status == 404
    assert hidden["type"] == "platform.tenant_not_found"
    assert audit == (
        "tenant.cross_scope_probe_denied",
        second["tenantId"],
        hidden["correlationId"],
    )


def test_invalid_or_membershipless_session_returns_authentication_required(
    postgres_connection: psycopg.Connection[tuple[object, ...]],
    api_base_url: str,
) -> None:
    slug = f"membership-{uuid4().hex}"
    created_status, created, headers = http_json(
        "POST",
        f"{api_base_url}/api/v1/tenants/register",
        payload=registration_payload(slug),
    )
    cookie = headers["set-cookie"].split(";", 1)[0]

    invalid_status, invalid, _invalid_headers = http_json(
        "GET",
        f"{api_base_url}/api/v1/session/tenant",
        cookie="gl_session=invalid",
    )
    with postgres_connection.transaction():
        postgres_connection.execute(
            "delete from platform_memberships where tenant_id = %s and user_id = %s",
            (created["tenantId"], created["actorId"]),
        )
        session_count = postgres_connection.execute(
            "select count(*) from platform_sessions where tenant_id = %s",
            (created["tenantId"],),
        ).fetchone()
    removed_status, removed, _removed_headers = http_json(
        "GET",
        f"{api_base_url}/api/v1/session/tenant",
        cookie=cookie,
    )

    assert created_status == 201
    assert invalid_status == 401
    assert invalid["type"] == "platform.authentication_required"
    assert session_count == (0,)
    assert removed_status == 401
    assert removed["type"] == "platform.authentication_required"


def test_runtime_database_identity_is_not_privileged(
    postgres_connection: psycopg.Connection[tuple[object, ...]],
    database_url: str,
) -> None:
    with psycopg.connect(database_url) as runtime_connection:
        runtime_user = runtime_connection.execute("select current_user").fetchone()
        assert runtime_user is not None
        with pytest.raises(psycopg.errors.InsufficientPrivilege):
            runtime_connection.execute("select count(*) from platform_tenants")

    with postgres_connection.transaction():
        attributes = postgres_connection.execute(
            """
            select rolsuper, rolbypassrls, rolinherit
            from pg_roles
            where rolname = %s
            """,
            (runtime_user[0],),
        ).fetchone()

    assert attributes == (False, False, False)


def test_rls_denies_tenant_tables_without_transaction_tenant_context(
    database_url: str,
) -> None:
    created = register(database_url, command(f"rls-{uuid4().hex}"))

    with psycopg.connect(database_url) as runtime_connection:
        with runtime_connection.transaction():
            runtime_connection.execute("set local role gastroledger_app")
            invisible = runtime_connection.execute(
                "select tenant_id from platform_tenant_settings where tenant_id = %s",
                (created.tenant_id,),
            ).fetchone()

    assert invisible is None
