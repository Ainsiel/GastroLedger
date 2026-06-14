from concurrent.futures import ThreadPoolExecutor
from uuid import uuid4

import psycopg

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


def test_session_scope_hides_another_tenant_and_records_denial_audit(
    postgres_connection: psycopg.Connection[tuple[object, ...]],
    database_url: str,
) -> None:
    first = register(database_url, command(f"first-{uuid4().hex}"))
    second = register(database_url, command(f"second-{uuid4().hex}"))
    store = PostgresPlatformStore(database_url)

    visible = store.resolve_tenant(first.session_token, first.tenant_id, "visible-probe")
    hidden = store.resolve_tenant(first.session_token, second.tenant_id, "hidden-probe")

    with postgres_connection.transaction():
        audit = postgres_connection.execute(
            """
            select action, object_reference
            from control_audit_events
            where tenant_id = %s and correlation_id = 'hidden-probe'
            """,
            (first.tenant_id,),
        ).fetchone()

    assert visible is not None
    assert visible.tenant_id == first.tenant_id
    assert hidden is None
    assert audit == ("tenant.cross_scope_probe_denied", str(second.tenant_id))


def test_rls_denies_tenant_tables_without_transaction_tenant_context(
    postgres_connection: psycopg.Connection[tuple[object, ...]],
    database_url: str,
) -> None:
    created = register(database_url, command(f"rls-{uuid4().hex}"))

    with postgres_connection.transaction():
        postgres_connection.execute("set local role gastroledger_app")
        invisible = postgres_connection.execute(
            "select tenant_id from platform_tenant_settings where tenant_id = %s",
            (created.tenant_id,),
        ).fetchone()

    assert invisible is None
