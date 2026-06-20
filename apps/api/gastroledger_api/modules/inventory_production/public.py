from dataclasses import dataclass
from decimal import Decimal

from gastroledger_api.application.identifiers import EventId, TenantId, WarehouseId
from gastroledger_api.modules.inventory_production.application.production import (
    PostProductionBatch,
    ProductionAuthorizationDenied,
    ProductionBatchView,
    ProductionConflict,
    ProductionIdentity,
    ProductionInsufficientStock,
    ProductionNotFound,
    ProductionService,
)
from gastroledger_api.modules.inventory_production.domain.production import (
    ProductionValidationError,
)

MODULE_ID = "inventory_production"


@dataclass(frozen=True)
class InventoryPosting:
    tenant_id: TenantId
    source_reference: str
    posting_type: str


@dataclass(frozen=True)
class InventoryTransactionReference:
    tenant_id: TenantId
    transaction_id: str


@dataclass(frozen=True)
class AllocationRequest:
    tenant_id: TenantId
    warehouse_id: WarehouseId
    stock_item_id: str
    quantity: Decimal


@dataclass(frozen=True)
class AllocationOutcome:
    request: AllocationRequest
    allocation_reference: str


@dataclass(frozen=True)
class IngredientCostChanged:
    event_id: EventId
    tenant_id: TenantId
    ingredient_id: str


@dataclass(frozen=True)
class InventoryMovementFact:
    event_id: EventId
    tenant_id: TenantId
    transaction_id: str


@dataclass(frozen=True)
class InventoryCountFact:
    event_id: EventId
    tenant_id: TenantId
    count_id: str


__all__ = [
    "AllocationOutcome",
    "AllocationRequest",
    "IngredientCostChanged",
    "InventoryCountFact",
    "InventoryMovementFact",
    "InventoryPosting",
    "InventoryTransactionReference",
    "MODULE_ID",
    "PostProductionBatch",
    "ProductionAuthorizationDenied",
    "ProductionBatchView",
    "ProductionConflict",
    "ProductionIdentity",
    "ProductionInsufficientStock",
    "ProductionNotFound",
    "ProductionService",
    "ProductionValidationError",
]
