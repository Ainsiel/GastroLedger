from dataclasses import dataclass
from decimal import Decimal

from gastroledger_api.application.identifiers import TenantId

MODULE_ID = "menu_engineering"


@dataclass(frozen=True)
class ApprovedRecipeVersionReference:
    tenant_id: TenantId
    recipe_version_id: str


@dataclass(frozen=True)
class ApprovedRecipeVersionSnapshot:
    reference: ApprovedRecipeVersionReference
    version: str


@dataclass(frozen=True)
class UnitConversionRequest:
    tenant_id: TenantId
    source_unit_id: str
    target_unit_id: str
    quantity: Decimal


@dataclass(frozen=True)
class UnitConversionResult:
    quantity: Decimal
    target_unit_id: str

