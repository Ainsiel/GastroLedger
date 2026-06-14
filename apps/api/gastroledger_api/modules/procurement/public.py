from dataclasses import dataclass

from gastroledger_api.application.identifiers import EventId, TenantId

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

