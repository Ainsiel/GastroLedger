from dataclasses import dataclass

from gastroledger_api.application.identifiers import ActorId, BranchId, TenantId, WarehouseId
from gastroledger_api.modules.platform_organization.application.registration import (
    AuthenticationRequired,
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
    "AuthenticationRequired",
    "BranchReference",
    "MODULE_ID",
    "RegisterTenant",
    "RegistrationCommand",
    "RegistrationConflict",
    "RegistrationValidationError",
    "ScryptPasswordHasher",
    "SessionTokenIssuer",
    "TenantReference",
    "WarehouseReference",
]

