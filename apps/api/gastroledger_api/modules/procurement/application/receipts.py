from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Protocol

from gastroledger_api.modules.procurement.application.suppliers import (
    ProcurementAuthorizationDenied,
    SupplierIdentity,
)
from gastroledger_api.modules.procurement.domain.receipts import (
    ValidatedSupplierReceipt,
    validate_supplier_receipt,
)


@dataclass(frozen=True)
class CreateSupplierReceiptLine:
    ingredient_id: str
    purchase_unit_id: str
    lot_code: str
    ordered_quantity: str
    delivered_quantity: str
    unit_cost: str
    expiry_date: date
    temperature: str
    minimum_temperature: str
    maximum_temperature: str
    tolerance_percent: str


@dataclass(frozen=True)
class CreateSupplierReceipt:
    idempotency_key: str
    order_reference: str
    supplier_id: str
    warehouse_id: str
    received_on: date
    lines: tuple[CreateSupplierReceiptLine, ...]


@dataclass(frozen=True)
class SupplierReceiptLineView:
    receipt_line_id: str
    lot_id: str | None
    lot_code: str
    accepted_quantity: Decimal
    remaining_quantity: Decimal
    status: str
    rejection_reason: str | None


@dataclass(frozen=True)
class SupplierReceiptView:
    receipt_id: str
    inventory_transaction_id: str | None
    idempotency_key: str
    order_reference: str
    status: str
    lines: tuple[SupplierReceiptLineView, ...]


class ProcurementReceiptStore(Protocol):
    def accept_supplier_receipt(
        self,
        identity: SupplierIdentity,
        receipt: ValidatedSupplierReceipt,
        correlation_id: str,
    ) -> SupplierReceiptView: ...


class ProcurementReceiptService:
    def __init__(self, *, store: ProcurementReceiptStore) -> None:
        self._store = store

    def accept_supplier_receipt(
        self,
        identity: SupplierIdentity,
        command: CreateSupplierReceipt,
        *,
        correlation_id: str,
    ) -> SupplierReceiptView:
        if identity.role not in {"tenant_admin", "branch_manager", "branch_operator"}:
            raise ProcurementAuthorizationDenied
        receipt = validate_supplier_receipt(
            idempotency_key=command.idempotency_key,
            order_reference=command.order_reference,
            supplier_id=command.supplier_id,
            warehouse_id=command.warehouse_id,
            received_on=command.received_on,
            lines=command.lines,
        )
        return self._store.accept_supplier_receipt(identity, receipt, correlation_id)
