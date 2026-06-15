from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

from psycopg import errors
from sqlalchemy import create_engine, func, select, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy.pool import NullPool

from gastroledger_api.application.identifiers import (
    ActorId,
    BranchId,
    TenantId,
    WarehouseId,
)
from gastroledger_api.modules.platform_organization.application.operating_scope import (
    BranchLimitExceeded,
    BranchView,
    OperatingAuthorizationDenied,
    OperatingCodeConflict,
    OperatingIdentity,
    OperatingNotFound,
    TenantSettingsView,
    WarehouseInactive,
    WarehouseView,
)
from gastroledger_api.modules.platform_organization.application.registration import (
    AuthenticationRequired,
    RegistrationConflict,
    TenantIdentity,
)
from gastroledger_api.modules.platform_organization.application.security import (
    SessionTokenIssuer,
)
from gastroledger_api.modules.platform_organization.domain.operating_scope import (
    ValidatedBranch,
    ValidatedTenantSettings,
    ValidatedWarehouse,
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
    PlatformWarehouse,
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
                            branch_limit=1,
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

    def update_settings(
        self,
        identity: OperatingIdentity,
        settings: ValidatedTenantSettings,
        correlation_id: str,
    ) -> TenantSettingsView:
        with self._open_session() as session, session.begin():
            self._authorize_operating_identity(session, identity)
            record = session.execute(
                select(PlatformTenantSetting)
                .where(PlatformTenantSetting.tenant_id == UUID(identity.tenant_id))
                .with_for_update()
            ).scalar_one()
            record.locale = settings.locale
            record.base_currency = settings.base_currency
            record.branch_limit = settings.branch_limit
            branch_count = self._branch_count(session, identity)
            self._audit(
                session,
                identity,
                correlation_id,
                "tenant.settings_updated",
                str(identity.tenant_id),
            )
            return TenantSettingsView(
                locale=record.locale,
                base_currency=record.base_currency,
                branch_limit=record.branch_limit,
                branch_count=branch_count,
            )

    def resolve_operating_identity(self, raw_session_token: str) -> OperatingIdentity:
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
            role = session.execute(
                select(PlatformMembership.role).where(
                    PlatformMembership.tenant_id == tenant_id,
                    PlatformMembership.user_id == actor_id,
                )
            ).scalar_one_or_none()
            if role is None:
                raise AuthenticationRequired
            return OperatingIdentity(
                tenant_id=TenantId(str(tenant_id)),
                actor_id=ActorId(str(actor_id)),
                role=role,
            )

    def get_settings(self, identity: OperatingIdentity) -> TenantSettingsView:
        with self._open_session() as session, session.begin():
            self._authorize_operating_identity(session, identity)
            settings = session.execute(
                select(PlatformTenantSetting).where(
                    PlatformTenantSetting.tenant_id == UUID(identity.tenant_id)
                )
            ).scalar_one()
            return TenantSettingsView(
                locale=settings.locale,
                base_currency=settings.base_currency,
                branch_limit=settings.branch_limit,
                branch_count=self._branch_count(session, identity),
            )

    def list_branches(self, identity: OperatingIdentity) -> tuple[BranchView, ...]:
        with self._open_session() as session, session.begin():
            self._authorize_operating_identity(session, identity)
            branches = session.execute(
                select(PlatformBranch)
                .where(PlatformBranch.tenant_id == UUID(identity.tenant_id))
                .order_by(PlatformBranch.code)
            ).scalars()
            warehouses = session.execute(
                select(PlatformWarehouse)
                .where(PlatformWarehouse.tenant_id == UUID(identity.tenant_id))
                .order_by(PlatformWarehouse.code)
            ).scalars()
            by_branch: dict[UUID, list[WarehouseView]] = {}
            for warehouse in warehouses:
                by_branch.setdefault(warehouse.branch_id, []).append(
                    self._warehouse_view(warehouse)
                )
            return tuple(
                BranchView(
                    branch_id=BranchId(str(branch.id)),
                    name=branch.name,
                    code=branch.code,
                    warehouses=tuple(by_branch.get(branch.id, [])),
                )
                for branch in branches
            )

    def create_branch(
        self,
        identity: OperatingIdentity,
        branch: ValidatedBranch,
        correlation_id: str,
    ) -> BranchView:
        branch_uuid = uuid4()
        try:
            with self._open_session() as session, session.begin():
                self._authorize_operating_identity(session, identity)
                setting = session.execute(
                    select(PlatformTenantSetting)
                    .where(PlatformTenantSetting.tenant_id == UUID(identity.tenant_id))
                    .with_for_update()
                ).scalar_one()
                if self._branch_count(session, identity) >= setting.branch_limit:
                    raise BranchLimitExceeded
                session.add(
                    PlatformBranch(
                        id=branch_uuid,
                        tenant_id=UUID(identity.tenant_id),
                        code=branch.code,
                        name=branch.name,
                    )
                )
                session.flush()
                self._audit(
                    session,
                    identity,
                    correlation_id,
                    "branch.created",
                    str(branch_uuid),
                )
        except IntegrityError as error:
            if isinstance(error.orig, errors.UniqueViolation):
                raise OperatingCodeConflict from error
            raise
        return BranchView(
            branch_id=BranchId(str(branch_uuid)),
            name=branch.name,
            code=branch.code,
        )

    def create_warehouse(
        self,
        identity: OperatingIdentity,
        branch_id: BranchId,
        warehouse: ValidatedWarehouse,
        correlation_id: str,
    ) -> WarehouseView:
        warehouse_uuid = uuid4()
        try:
            with self._open_session() as session, session.begin():
                self._authorize_operating_identity(session, identity)
                branch = session.execute(
                    select(PlatformBranch.id).where(
                        PlatformBranch.id == UUID(branch_id),
                        PlatformBranch.tenant_id == UUID(identity.tenant_id),
                    )
                ).scalar_one_or_none()
                if branch is None:
                    raise OperatingNotFound
                session.add(
                    PlatformWarehouse(
                        id=warehouse_uuid,
                        tenant_id=UUID(identity.tenant_id),
                        branch_id=UUID(branch_id),
                        code=warehouse.code,
                        name=warehouse.name,
                        type=warehouse.warehouse_type,
                        status="active",
                    )
                )
                session.flush()
                self._audit(
                    session,
                    identity,
                    correlation_id,
                    "warehouse.created",
                    str(warehouse_uuid),
                )
        except IntegrityError as error:
            if isinstance(error.orig, errors.UniqueViolation):
                raise OperatingCodeConflict from error
            raise
        return WarehouseView(
            warehouse_id=WarehouseId(str(warehouse_uuid)),
            branch_id=branch_id,
            name=warehouse.name,
            code=warehouse.code,
            warehouse_type=warehouse.warehouse_type,
            status="active",
        )

    def deactivate_warehouse(
        self,
        identity: OperatingIdentity,
        warehouse_id: WarehouseId,
        correlation_id: str,
    ) -> WarehouseView:
        with self._open_session() as session, session.begin():
            self._authorize_operating_identity(session, identity)
            warehouse = session.execute(
                select(PlatformWarehouse)
                .where(
                    PlatformWarehouse.id == UUID(warehouse_id),
                    PlatformWarehouse.tenant_id == UUID(identity.tenant_id),
                )
                .with_for_update()
            ).scalar_one_or_none()
            if warehouse is None:
                raise OperatingNotFound
            if warehouse.status == "inactive":
                raise WarehouseInactive
            warehouse.status = "inactive"
            self._audit(
                session,
                identity,
                correlation_id,
                "warehouse.deactivated",
                str(warehouse.id),
            )
            return self._warehouse_view(warehouse)

    @staticmethod
    def _authorize_operating_identity(
        session: Session,
        identity: OperatingIdentity,
    ) -> None:
        session.execute(text("set local role gastroledger_app"))
        session.execute(
            text("select set_config('app.current_tenant_id', :tenant_id, true)"),
            {"tenant_id": str(identity.tenant_id)},
        )
        role = session.execute(
            select(PlatformMembership.role).where(
                PlatformMembership.tenant_id == UUID(identity.tenant_id),
                PlatformMembership.user_id == UUID(identity.actor_id),
            )
        ).scalar_one_or_none()
        if role != "tenant_admin":
            raise OperatingAuthorizationDenied

    @staticmethod
    def _branch_count(session: Session, identity: OperatingIdentity) -> int:
        return int(
            session.execute(
                select(func.count()).select_from(PlatformBranch).where(
                    PlatformBranch.tenant_id == UUID(identity.tenant_id)
                )
            ).scalar_one()
        )

    @staticmethod
    def _audit(
        session: Session,
        identity: OperatingIdentity,
        correlation_id: str,
        action: str,
        object_reference: str,
    ) -> None:
        session.add(
            ControlAuditEvent(
                id=uuid4(),
                tenant_id=UUID(identity.tenant_id),
                actor_id=UUID(identity.actor_id),
                correlation_id=correlation_id,
                action=action,
                object_reference=object_reference,
                occurred_at=datetime.now(UTC),
            )
        )

    @staticmethod
    def _warehouse_view(warehouse: PlatformWarehouse) -> WarehouseView:
        return WarehouseView(
            warehouse_id=WarehouseId(str(warehouse.id)),
            branch_id=BranchId(str(warehouse.branch_id)),
            name=warehouse.name,
            code=warehouse.code,
            warehouse_type=warehouse.type,
            status=warehouse.status,
        )
