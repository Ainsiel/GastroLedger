from dataclasses import dataclass

from gastroledger_api.application.identifiers import ActorId, BranchId, TenantId, WarehouseId

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

