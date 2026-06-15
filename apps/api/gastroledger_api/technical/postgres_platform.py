from datetime import UTC, datetime, timedelta
from uuid import uuid4

import psycopg
from psycopg import errors

from gastroledger_api.application.identifiers import ActorId, BranchId, TenantId
from gastroledger_api.modules.platform_organization.application.registration import (
    AuthenticationRequired,
    RegistrationConflict,
    TenantIdentity,
)
from gastroledger_api.modules.platform_organization.application.security import SessionTokenIssuer
from gastroledger_api.modules.platform_organization.domain.registration import ValidatedRegistration


class PostgresPlatformStore:
    def __init__(self, database_url: str) -> None:
        self._database_url = database_url

    def register(
        self,
        registration: ValidatedRegistration,
        password_hash: str,
        session_hash: str,
    ) -> tuple[TenantId, ActorId, BranchId | None]:
        tenant_id = TenantId(str(uuid4()))
        actor_id = ActorId(str(uuid4()))
        branch_id = BranchId(str(uuid4())) if registration.branch_code else None
        expires_at = datetime.now(UTC) + timedelta(hours=8)

        try:
            with psycopg.connect(self._database_url) as connection:
                with connection.transaction():
                    connection.execute("set local role gastroledger_registration")
                    connection.execute(
                        "insert into platform_tenants (id, slug, name) values (%s, %s, %s)",
                        (tenant_id, registration.tenant_slug, registration.tenant_name),
                    )
                    connection.execute(
                        "insert into platform_tenant_settings (tenant_id) values (%s)",
                        (tenant_id,),
                    )
                    connection.execute(
                        """
                        insert into platform_users (id, normalized_login, password_hash)
                        values (%s, %s, %s)
                        """,
                        (actor_id, registration.admin_email, password_hash),
                    )
                    connection.execute(
                        """
                        insert into platform_memberships (tenant_id, user_id, role)
                        values (%s, %s, 'tenant_admin')
                        """,
                        (tenant_id, actor_id),
                    )
                    if branch_id:
                        connection.execute(
                            """
                            insert into platform_branches (id, tenant_id, code, name)
                            values (%s, %s, %s, %s)
                            """,
                            (
                                branch_id,
                                tenant_id,
                                registration.branch_code,
                                registration.branch_name,
                            ),
                        )
                    connection.execute(
                        """
                        insert into platform_sessions
                            (id, tenant_id, user_id, token_hash, expires_at)
                        values (%s, %s, %s, %s, %s)
                        """,
                        (str(uuid4()), tenant_id, actor_id, session_hash, expires_at),
                    )
        except errors.UniqueViolation as error:
            raise RegistrationConflict from error

        return tenant_id, actor_id, branch_id

    def resolve_tenant(
        self,
        raw_session_token: str,
        requested_tenant_id: str | None,
        correlation_id: str,
    ) -> TenantIdentity | None:
        token_hash = SessionTokenIssuer().hash(raw_session_token)
        with psycopg.connect(self._database_url) as connection:
            with connection.transaction():
                connection.execute("set local role gastroledger_session_resolver")
                session = connection.execute(
                    """
                    select tenant_id, user_id
                    from platform_sessions
                    where token_hash = %s and revoked_at is null and expires_at > now()
                    """,
                    (token_hash,),
                ).fetchone()
                if not session:
                    raise AuthenticationRequired
                tenant_id, actor_id = session
                connection.execute("set local role gastroledger_app")
                connection.execute(
                    "select set_config('app.current_tenant_id', %s, true)",
                    (str(tenant_id),),
                )
                membership = connection.execute(
                    """
                    select 1
                    from platform_memberships
                    where tenant_id = %s and user_id = %s
                    """,
                    (tenant_id, actor_id),
                ).fetchone()
                if not membership:
                    raise AuthenticationRequired
                if requested_tenant_id and requested_tenant_id != str(tenant_id):
                    connection.execute(
                        """
                        insert into control_audit_events (
                            id, tenant_id, actor_id, correlation_id, action, object_reference
                        ) values (%s, %s, %s, %s, %s, %s)
                        """,
                        (
                            str(uuid4()),
                            tenant_id,
                            actor_id,
                            correlation_id,
                            "tenant.cross_scope_probe_denied",
                            requested_tenant_id,
                        ),
                    )
                    return None
                tenant = connection.execute(
                    "select id, name, slug from platform_tenants where id = %s",
                    (tenant_id,),
                ).fetchone()
                if not tenant:
                    return None
                return TenantIdentity(
                    tenant_id=TenantId(str(tenant[0])),
                    actor_id=ActorId(str(actor_id)),
                    tenant_name=str(tenant[1]),
                    tenant_slug=str(tenant[2]),
                )
