from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Protocol


class ProductionAuthorizationDenied(Exception):
    pass


class ProductionNotFound(Exception):
    pass


class ProductionInsufficientStock(Exception):
    pass


class ProductionConflict(Exception):
    pass


@dataclass(frozen=True)
class ProductionIdentity:
    tenant_id: str
    actor_id: str
    role: str


@dataclass(frozen=True)
class PostProductionBatch:
    idempotency_key: str
    batch_number: str
    warehouse_id: str
    recipe_version_id: str
    actual_yield: str
    output_lot_code: str
    produced_on: date
    variance_reason: str


@dataclass(frozen=True)
class ProductionBatchView:
    production_batch_id: str
    inventory_transaction_id: str
    output_lot_id: str
    batch_number: str
    status: str
    recipe_version_id: str
    expected_yield: Decimal
    actual_yield: Decimal
    variance_quantity: Decimal
    variance_reason: str | None
    consumed_quantity: Decimal


class ProductionStore(Protocol):
    def post_batch(
        self,
        identity: ProductionIdentity,
        command: PostProductionBatch,
        correlation_id: str,
    ) -> ProductionBatchView: ...


class ProductionService:
    def __init__(self, *, store: ProductionStore) -> None:
        self._store = store

    def post_batch(
        self,
        identity: ProductionIdentity,
        command: PostProductionBatch,
        *,
        correlation_id: str,
    ) -> ProductionBatchView:
        if identity.role not in {"tenant_admin", "branch_manager", "branch_operator"}:
            raise ProductionAuthorizationDenied
        return self._store.post_batch(identity, command, correlation_id)
