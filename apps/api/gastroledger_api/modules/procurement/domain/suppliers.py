import re
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation

CODE_PATTERN = re.compile(r"^[A-Z0-9]+(?:-[A-Z0-9]+)*$")
CURRENCY_PATTERN = re.compile(r"^[A-Z]{3}$")


@dataclass(frozen=True)
class ProcurementValidationDetail:
    field: str
    code: str


@dataclass(frozen=True)
class ProcurementValidationError(Exception):
    details: tuple[ProcurementValidationDetail, ...]


@dataclass(frozen=True)
class ValidatedSupplier:
    name: str
    code: str


@dataclass(frozen=True)
class ValidatedSupplierOffer:
    supplier_id: str
    ingredient_id: str
    purchase_unit_id: str
    price: Decimal
    currency: str
    effective_from: date
    effective_until: date | None


def _normalize_name_and_code(
    *, name: str, code: str
) -> tuple[str, str, list[ProcurementValidationDetail]]:
    normalized_name = name.strip()
    normalized_code = code.strip().upper()
    details: list[ProcurementValidationDetail] = []
    if not normalized_name or len(normalized_name) > 120:
        details.append(ProcurementValidationDetail("name", "invalid"))
    if not CODE_PATTERN.fullmatch(normalized_code) or len(normalized_code) > 63:
        details.append(ProcurementValidationDetail("code", "invalid"))
    return normalized_name, normalized_code, details


def _parse_positive_decimal(
    value: str,
    field: str,
) -> tuple[Decimal | None, ProcurementValidationDetail | None]:
    try:
        parsed = Decimal(str(value).strip())
    except (InvalidOperation, ValueError):
        return None, ProcurementValidationDetail(field, "decimal_required")
    if not parsed.is_finite():
        return None, ProcurementValidationDetail(field, "decimal_required")
    if parsed <= 0:
        return None, ProcurementValidationDetail(field, "positive_required")
    return parsed, None


def validate_supplier(*, name: str, code: str) -> ValidatedSupplier:
    normalized_name, normalized_code, details = _normalize_name_and_code(
        name=name,
        code=code,
    )
    if details:
        raise ProcurementValidationError(tuple(details))
    return ValidatedSupplier(name=normalized_name, code=normalized_code)


def validate_supplier_offer(
    *,
    supplier_id: str,
    ingredient_id: str,
    purchase_unit_id: str,
    price: str,
    currency: str,
    effective_from: date,
    effective_until: date | None,
) -> ValidatedSupplierOffer:
    details: list[ProcurementValidationDetail] = []
    normalized_supplier_id = supplier_id.strip()
    normalized_ingredient_id = ingredient_id.strip()
    normalized_purchase_unit_id = purchase_unit_id.strip()
    normalized_currency = currency.strip().upper()
    if not normalized_supplier_id:
        details.append(ProcurementValidationDetail("supplierId", "required"))
    if not normalized_ingredient_id:
        details.append(ProcurementValidationDetail("ingredientId", "required"))
    if not normalized_purchase_unit_id:
        details.append(ProcurementValidationDetail("purchaseUnitId", "required"))
    parsed_price, price_error = _parse_positive_decimal(price, "price")
    if price_error:
        details.append(price_error)
    if not CURRENCY_PATTERN.fullmatch(normalized_currency):
        details.append(ProcurementValidationDetail("currency", "invalid"))
    if effective_until is not None and effective_until < effective_from:
        details.append(ProcurementValidationDetail("effectiveUntil", "before_effective_from"))
    if details:
        raise ProcurementValidationError(tuple(details))
    return ValidatedSupplierOffer(
        supplier_id=normalized_supplier_id,
        ingredient_id=normalized_ingredient_id,
        purchase_unit_id=normalized_purchase_unit_id,
        price=parsed_price or Decimal("0"),
        currency=normalized_currency,
        effective_from=effective_from,
        effective_until=effective_until,
    )
