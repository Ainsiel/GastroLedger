from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation

from gastroledger_api.modules.procurement.domain.suppliers import (
    ProcurementValidationDetail,
    ProcurementValidationError,
    _parse_positive_decimal,
)


@dataclass(frozen=True)
class ValidatedSupplierReceiptLine:
    ingredient_id: str
    purchase_unit_id: str
    lot_code: str
    ordered_quantity: Decimal
    delivered_quantity: Decimal
    accepted_quantity: Decimal
    remaining_quantity: Decimal
    unit_cost: Decimal
    expiry_date: date
    temperature: Decimal
    minimum_temperature: Decimal
    maximum_temperature: Decimal
    tolerance_percent: Decimal
    status: str
    rejection_reason: str | None


@dataclass(frozen=True)
class ValidatedSupplierReceipt:
    idempotency_key: str
    order_reference: str
    supplier_id: str
    warehouse_id: str
    received_on: date
    lines: tuple[ValidatedSupplierReceiptLine, ...]


def _parse_non_negative_decimal(
    value: str, field: str
) -> tuple[Decimal | None, ProcurementValidationDetail | None]:
    parsed, error = _parse_positive_decimal(value, field)
    if str(value).strip() == "0":
        return Decimal("0"), None
    return parsed, error


def _parse_decimal(
    value: str, field: str
) -> tuple[Decimal | None, ProcurementValidationDetail | None]:
    try:
        parsed = Decimal(str(value).strip())
    except (InvalidOperation, ValueError):
        return None, ProcurementValidationDetail(field, "decimal_required")
    if not parsed.is_finite():
        return None, ProcurementValidationDetail(field, "decimal_required")
    return parsed, None


def validate_supplier_receipt(
    *,
    idempotency_key: str,
    order_reference: str,
    supplier_id: str,
    warehouse_id: str,
    received_on: date,
    lines: tuple[object, ...],
) -> ValidatedSupplierReceipt:
    details: list[ProcurementValidationDetail] = []
    normalized_key = idempotency_key.strip()
    normalized_order = order_reference.strip()
    normalized_supplier = supplier_id.strip()
    normalized_warehouse = warehouse_id.strip()
    for field, value in (
        ("idempotencyKey", normalized_key),
        ("orderReference", normalized_order),
        ("supplierId", normalized_supplier),
        ("warehouseId", normalized_warehouse),
    ):
        if not value:
            details.append(ProcurementValidationDetail(field, "required"))
    if not lines:
        details.append(ProcurementValidationDetail("lines", "required"))

    validated: list[ValidatedSupplierReceiptLine] = []
    for index, line in enumerate(lines):
        prefix = f"lines[{index}]"
        ingredient_id = str(getattr(line, "ingredient_id", "")).strip()
        unit_id = str(getattr(line, "purchase_unit_id", "")).strip()
        lot_code = str(getattr(line, "lot_code", "")).strip().upper()
        if not ingredient_id:
            details.append(ProcurementValidationDetail(f"{prefix}.ingredientId", "required"))
        if not unit_id:
            details.append(ProcurementValidationDetail(f"{prefix}.purchaseUnitId", "required"))
        if not lot_code or len(lot_code) > 80:
            details.append(ProcurementValidationDetail(f"{prefix}.lotCode", "invalid"))
        values: dict[str, Decimal] = {}
        for attribute, field in (
            ("ordered_quantity", "orderedQuantity"),
            ("delivered_quantity", "deliveredQuantity"),
            ("unit_cost", "unitCost"),
        ):
            parsed, error = _parse_positive_decimal(
                str(getattr(line, attribute, "")), f"{prefix}.{field}"
            )
            if error:
                details.append(error)
            elif parsed is not None:
                values[attribute] = parsed
        for attribute, field in (
            ("temperature", "temperature"),
            ("minimum_temperature", "minimumTemperature"),
            ("maximum_temperature", "maximumTemperature"),
        ):
            parsed, error = _parse_decimal(
                str(getattr(line, attribute, "")), f"{prefix}.{field}"
            )
            if error:
                details.append(error)
            elif parsed is not None:
                values[attribute] = parsed
        tolerance, tolerance_error = _parse_non_negative_decimal(
            str(getattr(line, "tolerance_percent", "")),
            f"{prefix}.tolerancePercent",
        )
        if tolerance_error:
            details.append(tolerance_error)
        elif tolerance is not None:
            values["tolerance_percent"] = tolerance
        expiry_date = getattr(line, "expiry_date", received_on)
        if expiry_date <= received_on:
            details.append(ProcurementValidationDetail(f"{prefix}.expiryDate", "not_future"))
        required = {
            "ordered_quantity",
            "delivered_quantity",
            "unit_cost",
            "temperature",
            "minimum_temperature",
            "maximum_temperature",
            "tolerance_percent",
        }
        if not required.issubset(values) or not ingredient_id or not unit_id or not lot_code:
            continue
        status = "accepted"
        reason = None
        maximum_allowed = values["ordered_quantity"] * (
            Decimal("1") + values["tolerance_percent"] / Decimal("100")
        )
        if values["delivered_quantity"] > maximum_allowed:
            status, reason = "rejected", "quantity_above_tolerance"
        elif not (
            values["minimum_temperature"]
            <= values["temperature"]
            <= values["maximum_temperature"]
        ):
            status, reason = "rejected", "temperature_out_of_range"
        elif values["delivered_quantity"] < values["ordered_quantity"]:
            status = "partial"
        accepted = Decimal("0") if status == "rejected" else values["delivered_quantity"]
        validated.append(
            ValidatedSupplierReceiptLine(
                ingredient_id=ingredient_id,
                purchase_unit_id=unit_id,
                lot_code=lot_code,
                ordered_quantity=values["ordered_quantity"],
                delivered_quantity=values["delivered_quantity"],
                accepted_quantity=accepted,
                remaining_quantity=max(Decimal("0"), values["ordered_quantity"] - accepted),
                unit_cost=values["unit_cost"],
                expiry_date=expiry_date,
                temperature=values["temperature"],
                minimum_temperature=values["minimum_temperature"],
                maximum_temperature=values["maximum_temperature"],
                tolerance_percent=values["tolerance_percent"],
                status=status,
                rejection_reason=reason,
            )
        )
    if details:
        raise ProcurementValidationError(tuple(details))
    return ValidatedSupplierReceipt(
        normalized_key,
        normalized_order,
        normalized_supplier,
        normalized_warehouse,
        received_on,
        tuple(validated),
    )
