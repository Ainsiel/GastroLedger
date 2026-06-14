from dataclasses import dataclass
from typing import Protocol

from gastroledger_api.application.identifiers import ActorId, BranchId, TenantId
from gastroledger_api.modules.platform_organization.application.security import (
    ScryptPasswordHasher,
    SessionTokenIssuer,
)
from gastroledger_api.modules.platform_organization.domain.registration import (
    ValidatedRegistration,
    validate_registration,
)


@dataclass(frozen=True)
class RegistrationCommand:
    tenant_name: str
    tenant_slug: str
    admin_email: str
    password: str
    branch_name: str | None = None
    branch_code: str | None = None


@dataclass(frozen=True)
class RegistrationResult:
    tenant_id: TenantId
    actor_id: ActorId
    branch_id: BranchId | None
    tenant_name: str
    tenant_slug: str
    session_token: str


@dataclass(frozen=True)
class TenantIdentity:
    tenant_id: TenantId
    actor_id: ActorId
    tenant_name: str
    tenant_slug: str


class RegistrationConflict(Exception):
    pass


class PlatformStore(Protocol):
    def register(
        self,
        registration: ValidatedRegistration,
        password_hash: str,
        session_hash: str,
    ) -> tuple[TenantId, ActorId, BranchId | None]: ...


class RegisterTenant:
    def __init__(
        self,
        *,
        store: PlatformStore,
        password_hasher: ScryptPasswordHasher,
        session_tokens: SessionTokenIssuer,
    ) -> None:
        self._store = store
        self._password_hasher = password_hasher
        self._session_tokens = session_tokens

    def execute(self, command: RegistrationCommand) -> RegistrationResult:
        registration = validate_registration(
            tenant_name=command.tenant_name,
            tenant_slug=command.tenant_slug,
            admin_email=command.admin_email,
            password=command.password,
            branch_name=command.branch_name,
            branch_code=command.branch_code,
        )
        session = self._session_tokens.issue()
        tenant_id, actor_id, branch_id = self._store.register(
            registration,
            self._password_hasher.hash(registration.password),
            session.token_hash,
        )
        return RegistrationResult(
            tenant_id=tenant_id,
            actor_id=actor_id,
            branch_id=branch_id,
            tenant_name=registration.tenant_name,
            tenant_slug=registration.tenant_slug,
            session_token=session.raw_token,
        )
