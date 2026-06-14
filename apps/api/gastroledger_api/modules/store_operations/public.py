from collections.abc import Mapping
from dataclasses import dataclass

from gastroledger_api.application.identifiers import BranchId, EventId, TenantId

MODULE_ID = "store_operations"


@dataclass(frozen=True)
class ActiveMenuItemReference:
    tenant_id: TenantId
    menu_item_id: str
    recipe_version_id: str


@dataclass(frozen=True)
class SaleImportAccepted:
    event_id: EventId
    tenant_id: TenantId
    import_id: str


@dataclass(frozen=True)
class ClosedStoreOperationsFact:
    event_id: EventId
    tenant_id: TenantId
    branch_id: BranchId
    fact_type: str


@dataclass(frozen=True)
class ImportRow:
    row_number: int
    values: Mapping[str, str]
