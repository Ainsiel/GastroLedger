import re
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation

SUPPORTED_DIMENSIONS = {"count", "mass", "volume"}
CODE_PATTERN = re.compile(r"^[A-Z0-9]+(?:-[A-Z0-9]+)*$")


@dataclass(frozen=True)
class MenuValidationDetail:
    field: str
    code: str


@dataclass(frozen=True)
class MenuValidationError(Exception):
    details: tuple[MenuValidationDetail, ...]


@dataclass(frozen=True)
class ValidatedUnit:
    name: str
    code: str
    dimension: str


@dataclass(frozen=True)
class ValidatedConversionFactor:
    source_unit_id: str
    target_unit_id: str
    factor: Decimal
    effective_from: date


@dataclass(frozen=True)
class ValidatedIngredient:
    name: str
    code: str
    purchase_unit_id: str
    consumption_unit_id: str
    shelf_life_days: int
    critical_stock_quantity: Decimal


def _normalize_name_and_code(
    *, name: str, code: str
) -> tuple[str, str, list[MenuValidationDetail]]:
    normalized_name = name.strip()
    normalized_code = code.strip().upper()
    details: list[MenuValidationDetail] = []
    if not normalized_name or len(normalized_name) > 120:
        details.append(MenuValidationDetail("name", "invalid"))
    if not CODE_PATTERN.fullmatch(normalized_code) or len(normalized_code) > 63:
        details.append(MenuValidationDetail("code", "invalid"))
    return normalized_name, normalized_code, details


def _parse_positive_decimal(
    value: str,
    field: str,
) -> tuple[Decimal | None, MenuValidationDetail | None]:
    try:
        parsed = Decimal(str(value).strip())
    except (InvalidOperation, ValueError):
        return None, MenuValidationDetail(field, "decimal_required")
    if not parsed.is_finite():
        return None, MenuValidationDetail(field, "decimal_required")
    if parsed <= 0:
        return None, MenuValidationDetail(field, "positive_required")
    return parsed, None


def validate_unit(*, name: str, code: str, dimension: str) -> ValidatedUnit:
    normalized_name, normalized_code, details = _normalize_name_and_code(
        name=name, code=code
    )
    normalized_dimension = dimension.strip().lower()
    if normalized_dimension not in SUPPORTED_DIMENSIONS:
        details.append(MenuValidationDetail("dimension", "unsupported"))
    if details:
        raise MenuValidationError(tuple(details))
    return ValidatedUnit(
        name=normalized_name,
        code=normalized_code,
        dimension=normalized_dimension,
    )


def validate_conversion_factor(
    *,
    source_unit_id: str,
    target_unit_id: str,
    factor: str,
    effective_from: date,
) -> ValidatedConversionFactor:
    details: list[MenuValidationDetail] = []
    source = source_unit_id.strip()
    target = target_unit_id.strip()
    if not source:
        details.append(MenuValidationDetail("sourceUnitId", "required"))
    if not target:
        details.append(MenuValidationDetail("targetUnitId", "required"))
    if source and target and source == target:
        details.append(MenuValidationDetail("targetUnitId", "same_unit"))
    parsed_factor, factor_error = _parse_positive_decimal(factor, "factor")
    if factor_error:
        details.append(factor_error)
    if details:
        raise MenuValidationError(tuple(details))
    return ValidatedConversionFactor(
        source_unit_id=source,
        target_unit_id=target,
        factor=parsed_factor or Decimal("1"),
        effective_from=effective_from,
    )


def validate_ingredient(
    *,
    name: str,
    code: str,
    purchase_unit_id: str,
    consumption_unit_id: str,
    shelf_life_days: int,
    critical_stock_quantity: str,
) -> ValidatedIngredient:
    normalized_name, normalized_code, details = _normalize_name_and_code(
        name=name, code=code
    )
    purchase_unit = purchase_unit_id.strip()
    consumption_unit = consumption_unit_id.strip()
    if not purchase_unit:
        details.append(MenuValidationDetail("purchaseUnitId", "required"))
    if not consumption_unit:
        details.append(MenuValidationDetail("consumptionUnitId", "required"))
    if type(shelf_life_days) is not int:
        details.append(MenuValidationDetail("shelfLifeDays", "invalid_integer"))
    elif shelf_life_days < 1 or shelf_life_days > 3650:
        details.append(MenuValidationDetail("shelfLifeDays", "out_of_range"))
    parsed_quantity, quantity_error = _parse_positive_decimal(
        critical_stock_quantity,
        "criticalStockQuantity",
    )
    if quantity_error:
        details.append(quantity_error)
    if details:
        raise MenuValidationError(tuple(details))
    return ValidatedIngredient(
        name=normalized_name,
        code=normalized_code,
        purchase_unit_id=purchase_unit,
        consumption_unit_id=consumption_unit,
        shelf_life_days=shelf_life_days,
        critical_stock_quantity=parsed_quantity or Decimal("0"),
    )
