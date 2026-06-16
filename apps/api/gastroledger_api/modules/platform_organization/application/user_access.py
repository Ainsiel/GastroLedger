from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Protocol

from gastroledger_api.modules.platform_organization.application.operating_scope import (
    OperatingAuthorizationDenied,
    OperatingIdentity,
)
from gastroledger_api.modules.platform_organization.application.security import (
    ScryptPasswordHasher,
    SessionTokenIssuer,
)
from gastroledger_api.modules.platform_organization.domain.user_access import (
    ValidatedInvitation,
    validate_invitation,
)


@dataclass(frozen=True)
class InviteLocalUser:
    invitee_login: str
    role: str
    scope: str
    branch_id: str | None
    ttl_hours: int = 24


@dataclass(frozen=True)
class AcceptInvitation:
    manual_share_token: str
    password: str


class PrivilegeEscalationDenied(Exception):
    pass


class InvitationExpired(Exception):
    pass


class InvitationSingleUseViolation(Exception):
    pass


class InvitationNotFound(Exception):
    pass


class UserAccessStore(Protocol):
    def create_invitation(
        self,
        identity: OperatingIdentity,
        invitation: ValidatedInvitation,
        token_hash: str,
        expires_at: datetime,
        correlation_id: str,
    ) -> object: ...

    def accept_invitation(
        self,
        command: AcceptInvitation,
        token_hash: str,
        password_hash: str,
        correlation_id: str,
    ) -> object: ...

    def list_visible_branches(self, identity: OperatingIdentity) -> tuple[str, ...]: ...


class UserAccessService:
    def __init__(
        self,
        *,
        store: UserAccessStore,
        password_hasher: ScryptPasswordHasher | None = None,
        invitation_tokens: SessionTokenIssuer | None = None,
    ) -> None:
        self._store = store
        self._password_hasher = password_hasher or ScryptPasswordHasher()
        self._invitation_tokens = invitation_tokens or SessionTokenIssuer()

    def invite_local_user(
        self,
        identity: OperatingIdentity,
        command: InviteLocalUser,
        *,
        correlation_id: str,
    ) -> object:
        if identity.role != "tenant_admin":
            raise OperatingAuthorizationDenied
        invitation = validate_invitation(
            invitee_login=command.invitee_login,
            role=command.role,
            scope=command.scope,
            branch_id=command.branch_id,
            ttl_hours=command.ttl_hours,
        )
        if invitation.role == "tenant_admin":
            raise PrivilegeEscalationDenied

        issued = self._invitation_tokens.issue()
        expires_at = datetime.now(UTC) + timedelta(hours=invitation.ttl_hours)
        created = self._store.create_invitation(
            identity,
            invitation,
            issued.token_hash,
            expires_at,
            correlation_id,
        )
        if isinstance(created, dict):
            return {**created, "manualShareToken": issued.raw_token}
        return created

    def accept_invitation(
        self,
        command: AcceptInvitation,
        *,
        correlation_id: str,
    ) -> object:
        token_hash = self._invitation_tokens.hash(command.manual_share_token)
        password_hash = self._password_hasher.hash(command.password)
        return self._store.accept_invitation(
            command,
            token_hash,
            password_hash,
            correlation_id,
        )

    def ensure_invitation_usable(
        self,
        *,
        expires_at: datetime,
        accepted_at: datetime | None,
    ) -> None:
        if accepted_at is not None:
            raise InvitationSingleUseViolation
        if expires_at <= datetime.now(UTC):
            raise InvitationExpired

    def list_visible_branches(self, identity: OperatingIdentity) -> tuple[str, ...]:
        return self._store.list_visible_branches(identity)
