from dataclasses import dataclass

from gastroledger_api.application.identifiers import (
    ActorId,
    BranchId,
    TenantId,
    WarehouseId,
)
from gastroledger_api.modules.platform_organization.application.operating_scope import (
    BranchLimitExceeded,
    BranchView,
    CreateBranch,
    CreateWarehouse,
    DeactivateWarehouse,
    OperatingAuthorizationDenied,
    OperatingCodeConflict,
    OperatingIdentity,
    OperatingNotFound,
    OperatingScopeService,
    TenantSettingsView,
    UpdateTenantSettings,
    WarehouseDeactivationUnsafe,
    WarehouseInactive,
    WarehouseMovementGuard,
    WarehouseView,
)
from gastroledger_api.modules.platform_organization.application.registration import (
    AuthenticationRequired,
    RegisterTenant,
    RegistrationCommand,
    RegistrationConflict,
)
from gastroledger_api.modules.platform_organization.application.security import (
    InvalidCredentials,
    ScryptPasswordHasher,
    SessionLoginResult,
    SessionTokenIssuer,
    TenantLoginAmbiguous,
)
from gastroledger_api.modules.platform_organization.application.user_access import (
    AcceptInvitation,
    InvitationExpired,
    InvitationNotFound,
    InvitationSingleUseViolation,
    InviteLocalUser,
    PrivilegeEscalationDenied,
    UserAccessService,
)
from gastroledger_api.modules.platform_organization.domain.operating_scope import (
    OperatingValidationError,
    validate_branch,
    validate_tenant_settings,
    validate_warehouse,
)
from gastroledger_api.modules.platform_organization.domain.registration import (
    RegistrationValidationError,
)
from gastroledger_api.modules.platform_organization.domain.user_access import (
    UserAccessValidationError,
    validate_invitation,
)

MODULE_ID = "platform_organization"


@dataclass(frozen=True)
class TenantReference:
    tenant_id: TenantId


@dataclass(frozen=True)
class ActorReference:
    actor_id: ActorId
    tenant_id: TenantId


@dataclass(frozen=True)
class BranchReference:
    branch_id: BranchId
    tenant_id: TenantId


@dataclass(frozen=True)
class WarehouseReference:
    warehouse_id: WarehouseId
    branch_id: BranchId
    tenant_id: TenantId


__all__ = [
    "ActorReference",
    "AcceptInvitation",
    "AuthenticationRequired",
    "BranchReference",
    "BranchLimitExceeded",
    "BranchView",
    "CreateBranch",
    "CreateWarehouse",
    "DeactivateWarehouse",
    "InvalidCredentials",
    "InvitationExpired",
    "InvitationNotFound",
    "InvitationSingleUseViolation",
    "InviteLocalUser",
    "MODULE_ID",
    "OperatingAuthorizationDenied",
    "OperatingCodeConflict",
    "OperatingIdentity",
    "OperatingNotFound",
    "OperatingScopeService",
    "OperatingValidationError",
    "PrivilegeEscalationDenied",
    "RegisterTenant",
    "RegistrationCommand",
    "RegistrationConflict",
    "RegistrationValidationError",
    "ScryptPasswordHasher",
    "SessionLoginResult",
    "SessionTokenIssuer",
    "TenantLoginAmbiguous",
    "TenantReference",
    "TenantSettingsView",
    "UpdateTenantSettings",
    "UserAccessService",
    "UserAccessValidationError",
    "WarehouseReference",
    "WarehouseDeactivationUnsafe",
    "WarehouseInactive",
    "WarehouseMovementGuard",
    "WarehouseView",
    "validate_branch",
    "validate_invitation",
    "validate_tenant_settings",
    "validate_warehouse",
]

