from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

from psycopg import errors
from sqlalchemy import create_engine, select, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy.pool import NullPool

from gastroledger_api.application.identifiers import ActorId, BranchId, TenantId
from gastroledger_api.modules.platform_organization.application.registration import (
    AuthenticationRequired,
    RegistrationConflict,
    TenantIdentity,
)
from gastroledger_api.modules.platform_organization.application.security import (
    SessionTokenIssuer,
)
from gastroledger_api.modules.platform_organization.domain.registration import (
    ValidatedRegistration,
)
from gastroledger_api.technical.platform_models import (
    ControlAuditEvent,
    PlatformBranch,
    PlatformMembership,
    PlatformSession,
    PlatformTenant,
    PlatformTenantSetting,
    PlatformUser,
)


def sqlalchemy_database_url(database_url: str) -> str:
    if database_url.startswith("postgresql://"):
        return database_url.replace("postgresql://", "postgresql+psycopg://", 1)
    return database_url


class PostgresPlatformStore:
    def __init__(self, database_url: str) -> None:
        self._database_url = database_url
        self._engine: Engine | None = None

    def _open_session(self) -> Session:
        if self._engine is None:
            self._engine = create_engine(
                sqlalchemy_database_url(self._database_url), poolclass=NullPool
            )
        return Session(self._engine)

    def register(
        self,
        registration: ValidatedRegistration,
        password_hash: str,
        session_hash: str,
    ) -> tuple[TenantId, ActorId, BranchId | None]:
        tenant_uuid = uuid4()
        actor_uuid = uuid4()
        branch_uuid = uuid4() if registration.branch_code else None
        expires_at = datetime.now(UTC) + timedelta(hours=8)

        try:
            with self._open_session() as session, session.begin():
                session.execute(text("set local role gastroledger_registration"))
                session.add_all(
                    [
                        PlatformTenant(
                            id=tenant_uuid,
                            slug=registration.tenant_slug,
                            name=registration.tenant_name,
                            status="active",
                            created_at=datetime.now(UTC),
                        ),
                        PlatformUser(
                            id=actor_uuid,
                            normalized_login=registration.admin_email,
                            password_hash=password_hash,
                            created_at=datetime.now(UTC),
                        ),
                    ]
                )
                session.flush()

                session.add_all(
                    [
                        PlatformTenantSetting(
                            tenant_id=tenant_uuid,
                            locale="en",
                            base_currency="USD",
                        ),
                        PlatformMembership(
                            tenant_id=tenant_uuid,
                            user_id=actor_uuid,
                            role="tenant_admin",
                        ),
                    ]
                )
                if branch_uuid:
                    session.add(
                        PlatformBranch(
                            id=branch_uuid,
                            tenant_id=tenant_uuid,
                            code=registration.branch_code or "",
                            name=registration.branch_name or "",
                        )
                    )
                session.flush()

                session.add(
                    PlatformSession(
                        id=uuid4(),
                        tenant_id=tenant_uuid,
                        user_id=actor_uuid,
                        token_hash=session_hash,
                        expires_at=expires_at,
                        revoked_at=None,
                        created_at=datetime.now(UTC),
                    )
                )
        except IntegrityError as error:
            if isinstance(error.orig, errors.UniqueViolation):
                raise RegistrationConflict from error
            raise

        return (
            TenantId(str(tenant_uuid)),
            ActorId(str(actor_uuid)),
            BranchId(str(branch_uuid)) if branch_uuid else None,
        )

    def resolve_tenant(
        self,
        raw_session_token: str,
        requested_tenant_id: str | None,
        correlation_id: str,
    ) -> TenantIdentity | None:
        token_hash = SessionTokenIssuer().hash(raw_session_token)
        with self._open_session() as session, session.begin():
            session.execute(text("set local role gastroledger_session_resolver"))
            scoped_session = session.execute(
                select(PlatformSession.tenant_id, PlatformSession.user_id).where(
                    PlatformSession.token_hash == token_hash,
                    PlatformSession.revoked_at.is_(None),
                    PlatformSession.expires_at > datetime.now(UTC),
                )
            ).one_or_none()
            if not scoped_session:
                raise AuthenticationRequired

            tenant_id, actor_id = scoped_session
            session.execute(text("set local role gastroledger_app"))
            session.execute(
                text("select set_config('app.current_tenant_id', :tenant_id, true)"),
                {"tenant_id": str(tenant_id)},
            )
            membership = session.execute(
                select(PlatformMembership.user_id).where(
                    PlatformMembership.tenant_id == tenant_id,
                    PlatformMembership.user_id == actor_id,
                )
            ).first()
            if not membership:
                raise AuthenticationRequired

            target_tenant_id = UUID(requested_tenant_id) if requested_tenant_id else tenant_id
            tenant = session.execute(
                select(PlatformTenant.id, PlatformTenant.name, PlatformTenant.slug).where(
                    PlatformTenant.id == target_tenant_id
                )
            ).one_or_none()
            if not tenant and requested_tenant_id:
                session.add(
                    ControlAuditEvent(
                        id=uuid4(),
                        tenant_id=tenant_id,
                        actor_id=actor_id,
                        correlation_id=correlation_id,
                        action="tenant.cross_scope_probe_denied",
                        object_reference=requested_tenant_id,
                        occurred_at=datetime.now(UTC),
                    )
                )
                return None
            if not tenant:
                return None

            return TenantIdentity(
                tenant_id=TenantId(str(tenant.id)),
                actor_id=ActorId(str(actor_id)),
                tenant_name=tenant.name,
                tenant_slug=tenant.slug,
            )
