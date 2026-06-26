from dataclasses import dataclass

from gastroledger_api.application.identifiers import EventId, TenantId
from gastroledger_api.modules.procurement.application.receipts import (
    CreateSupplierReceipt,
    CreateSupplierReceiptLine,
    ProcurementReceiptService,
    SupplierReceiptLineView,
    SupplierReceiptView,
)
from gastroledger_api.modules.procurement.application.suppliers import (
    CreateSupplier,
    CreateSupplierOffer,
    ProcurementAuthorizationDenied,
    ProcurementCodeConflict,
    ProcurementDateOverlap,
    ProcurementNotFound,
    ProcurementService,
    ProcurementUnitMismatch,
    SupplierIdentity,
    SupplierOfferView,
    SupplierView,
)
from gastroledger_api.modules.procurement.domain.receipts import validate_supplier_receipt
from gastroledger_api.modules.procurement.domain.suppliers import (
    ProcurementValidationError,
    validate_supplier,
    validate_supplier_offer,
)

MODULE_ID = "procurement"


@dataclass(frozen=True)
class SupplierReceiptAccepted:
    event_id: EventId
    tenant_id: TenantId
    receipt_id: str


@dataclass(frozen=True)
class SupplierReturnAccepted:
    event_id: EventId
    tenant_id: TenantId
    return_id: str


__all__ = [
    "CreateSupplier",
    "CreateSupplierOffer",
    "CreateSupplierReceipt",
    "CreateSupplierReceiptLine",
    "MODULE_ID",
    "ProcurementAuthorizationDenied",
    "ProcurementCodeConflict",
    "ProcurementDateOverlap",
    "ProcurementNotFound",
    "ProcurementReceiptService",
    "ProcurementService",
    "ProcurementUnitMismatch",
    "ProcurementValidationError",
    "SupplierIdentity",
    "SupplierOfferView",
    "SupplierReceiptLineView",
    "SupplierReceiptView",
    "SupplierReceiptAccepted",
    "SupplierReturnAccepted",
    "SupplierView",
    "validate_supplier",
    "validate_supplier_offer",
    "validate_supplier_receipt",
]
