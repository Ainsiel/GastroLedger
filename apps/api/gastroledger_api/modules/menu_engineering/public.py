from dataclasses import dataclass
from decimal import Decimal

from gastroledger_api.application.identifiers import TenantId
from gastroledger_api.modules.menu_engineering.application.catalog import (
    ArchiveIngredient,
    ConversionFactorView,
    CreateConversionFactor,
    CreateIngredient,
    CreateUnit,
    IngredientArchived,
    IngredientCodeConflict,
    IngredientView,
    MenuAuthorizationDenied,
    MenuCatalogService,
    MenuCodeConflict,
    MenuIdentity,
    MenuNotFound,
    UnitConversionResult,
    UnitConversionUnavailable,
    UnitDimensionMismatch,
    UnitView,
)
from gastroledger_api.modules.menu_engineering.domain.catalog import (
    MenuValidationError,
    validate_conversion_factor,
    validate_ingredient,
    validate_unit,
)

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


__all__ = [
    "ArchiveIngredient",
    "ApprovedRecipeVersionReference",
    "ApprovedRecipeVersionSnapshot",
    "ConversionFactorView",
    "CreateConversionFactor",
    "CreateIngredient",
    "CreateUnit",
    "IngredientArchived",
    "IngredientCodeConflict",
    "IngredientView",
    "MODULE_ID",
    "MenuAuthorizationDenied",
    "MenuCatalogService",
    "MenuCodeConflict",
    "MenuIdentity",
    "MenuNotFound",
    "MenuValidationError",
    "UnitConversionResult",
    "UnitConversionRequest",
    "UnitConversionUnavailable",
    "UnitDimensionMismatch",
    "UnitView",
    "validate_conversion_factor",
    "validate_ingredient",
    "validate_unit",
]
