from dataclasses import dataclass
from typing import Protocol

from gastroledger_api.application.identifiers import ActorId, BranchId, TenantId, WarehouseId
from gastroledger_api.modules.platform_organization.domain.operating_scope import (
    ValidatedBranch,
    ValidatedTenantSettings,
    ValidatedWarehouse,
    validate_branch,
    validate_tenant_settings,
    validate_warehouse,
)


@dataclass(frozen=True)
class OperatingIdentity:
    tenant_id: TenantId
    actor_id: ActorId
    role: str


@dataclass(frozen=True)
class UpdateTenantSettings:
    locale: str
    base_currency: str
    branch_limit: int


@dataclass(frozen=True)
class CreateBranch:
    name: str
    code: str


@dataclass(frozen=True)
class CreateWarehouse:
    branch_id: BranchId
    name: str
    code: str
    warehouse_type: str


@dataclass(frozen=True)
class DeactivateWarehouse:
    warehouse_id: WarehouseId


class OperatingAuthorizationDenied(Exception):
    pass


class BranchLimitExceeded(Exception):
    pass


class OperatingCodeConflict(Exception):
    pass


class OperatingNotFound(Exception):
    pass


class WarehouseDeactivationUnsafe(Exception):
    pass


class WarehouseInactive(Exception):
    pass


@dataclass(frozen=True)
class TenantSettingsView:
    locale: str
    base_currency: str
    branch_limit: int
    branch_count: int


@dataclass(frozen=True)
class WarehouseView:
    warehouse_id: WarehouseId
    branch_id: BranchId
    name: str
    code: str
    warehouse_type: str
    status: str


@dataclass(frozen=True)
class BranchView:
    branch_id: BranchId
    name: str
    code: str
    warehouses: tuple[WarehouseView, ...] = ()


class OperatingStore(Protocol):
    def get_settings(self, identity: OperatingIdentity) -> TenantSettingsView: ...

    def list_branches(self, identity: OperatingIdentity) -> tuple[BranchView, ...]: ...

    def update_settings(
        self,
        identity: OperatingIdentity,
        settings: ValidatedTenantSettings,
        correlation_id: str,
    ) -> TenantSettingsView: ...

    def create_branch(
        self,
        identity: OperatingIdentity,
        branch: ValidatedBranch,
        correlation_id: str,
    ) -> BranchView: ...

    def create_warehouse(
        self,
        identity: OperatingIdentity,
        branch_id: BranchId,
        warehouse: ValidatedWarehouse,
        correlation_id: str,
    ) -> WarehouseView: ...

    def deactivate_warehouse(
        self,
        identity: OperatingIdentity,
        warehouse_id: WarehouseId,
        correlation_id: str,
    ) -> WarehouseView: ...


class WarehouseMovementGuard(Protocol):
    def has_open_movements(
        self, identity: OperatingIdentity, warehouse_id: WarehouseId
    ) -> bool: ...


class OperatingScopeService:
    def __init__(
        self, *, store: OperatingStore, movement_guard: WarehouseMovementGuard
    ) -> None:
        self._store = store
        self._movement_guard = movement_guard

    def update_settings(
        self,
        identity: OperatingIdentity,
        command: UpdateTenantSettings,
        *,
        correlation_id: str,
    ) -> TenantSettingsView:
        self._require_tenant_admin(identity)
        settings = validate_tenant_settings(
            locale=command.locale,
            base_currency=command.base_currency,
            branch_limit=command.branch_limit,
        )
        return self._store.update_settings(identity, settings, correlation_id)

    def get_settings(self, identity: OperatingIdentity) -> TenantSettingsView:
        self._require_tenant_admin(identity)
        return self._store.get_settings(identity)

    def list_branches(self, identity: OperatingIdentity) -> tuple[BranchView, ...]:
        self._require_tenant_admin(identity)
        return self._store.list_branches(identity)

    def create_branch(
        self,
        identity: OperatingIdentity,
        command: CreateBranch,
        *,
        correlation_id: str,
    ) -> BranchView:
        self._require_tenant_admin(identity)
        branch = validate_branch(name=command.name, code=command.code)
        return self._store.create_branch(identity, branch, correlation_id)

    def create_warehouse(
        self,
        identity: OperatingIdentity,
        command: CreateWarehouse,
        *,
        correlation_id: str,
    ) -> WarehouseView:
        self._require_tenant_admin(identity)
        warehouse = validate_warehouse(
            name=command.name,
            code=command.code,
            warehouse_type=command.warehouse_type,
        )
        return self._store.create_warehouse(
            identity,
            command.branch_id,
            warehouse,
            correlation_id,
        )

    def deactivate_warehouse(
        self,
        identity: OperatingIdentity,
        command: DeactivateWarehouse,
        *,
        correlation_id: str,
    ) -> WarehouseView:
        self._require_tenant_admin(identity)
        if self._movement_guard.has_open_movements(identity, command.warehouse_id):
            raise WarehouseDeactivationUnsafe
        return self._store.deactivate_warehouse(
            identity,
            command.warehouse_id,
            correlation_id,
        )

    @staticmethod
    def _require_tenant_admin(identity: OperatingIdentity) -> None:
        if identity.role != "tenant_admin":
            raise OperatingAuthorizationDenied
