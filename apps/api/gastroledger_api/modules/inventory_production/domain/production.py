from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal, InvalidOperation


@dataclass(frozen=True)
class ProductionValidationDetail:
    field: str
    code: str


class ProductionValidationError(Exception):
    def __init__(self, details: tuple[ProductionValidationDetail, ...]) -> None:
        super().__init__("invalid production batch")
        self.details = details


@dataclass(frozen=True)
class StockLot:
    lot_id: str
    available_quantity: Decimal
    expiry_date: date | None
    created_at: datetime


@dataclass(frozen=True)
class StockAllocation:
    lot_id: str
    quantity: Decimal


@dataclass(frozen=True)
class ValidatedProductionBatch:
    idempotency_key: str
    batch_number: str
    warehouse_id: str
    recipe_version_id: str
    actual_yield: Decimal
    output_lot_code: str
    produced_on: date
    variance_reason: str | None
    expected_yield: Decimal

    @property
    def variance_quantity(self) -> Decimal:
        return self.actual_yield - self.expected_yield


def _positive_decimal(
    value: str, field: str
) -> tuple[Decimal | None, ProductionValidationDetail | None]:
    try:
        parsed = Decimal(value)
    except (InvalidOperation, ValueError):
        return None, ProductionValidationDetail(field, "invalid")
    if not parsed.is_finite() or parsed <= 0:
        return None, ProductionValidationDetail(field, "must_be_positive")
    return parsed, None


def validate_production_batch(
    *,
    idempotency_key: str,
    batch_number: str,
    warehouse_id: str,
    recipe_version_id: str,
    actual_yield: str,
    output_lot_code: str,
    produced_on: date,
    variance_reason: str,
    expected_yield: Decimal,
) -> ValidatedProductionBatch:
    details: list[ProductionValidationDetail] = []
    values = {
        "idempotencyKey": idempotency_key.strip(),
        "batchNumber": batch_number.strip().upper(),
        "warehouseId": warehouse_id.strip(),
        "recipeVersionId": recipe_version_id.strip(),
        "outputLotCode": output_lot_code.strip().upper(),
    }
    for field, value in values.items():
        if not value:
            details.append(ProductionValidationDetail(field, "required"))
    parsed_yield, yield_error = _positive_decimal(actual_yield, "actualYield")
    if yield_error:
        details.append(yield_error)
    normalized_reason = variance_reason.strip()
    if parsed_yield is not None and parsed_yield < expected_yield and not normalized_reason:
        details.append(
            ProductionValidationDetail("varianceReason", "required_for_lower_yield")
        )
    if details:
        raise ProductionValidationError(tuple(details))
    return ValidatedProductionBatch(
        idempotency_key=values["idempotencyKey"],
        batch_number=values["batchNumber"],
        warehouse_id=values["warehouseId"],
        recipe_version_id=values["recipeVersionId"],
        actual_yield=parsed_yield or Decimal("0"),
        output_lot_code=values["outputLotCode"],
        produced_on=produced_on,
        variance_reason=normalized_reason or None,
        expected_yield=expected_yield,
    )


def allocate_stock(
    lots: tuple[StockLot, ...], required_quantity: Decimal
) -> tuple[StockAllocation, ...]:
    available = sum((lot.available_quantity for lot in lots), Decimal("0"))
    if required_quantity <= 0:
        raise ProductionValidationError(
            (ProductionValidationDetail("quantity", "must_be_positive"),)
        )
    if available < required_quantity:
        raise ProductionValidationError(
            (ProductionValidationDetail("stock", "insufficient_stock"),)
        )
    ordered = sorted(
        lots,
        key=lambda lot: (
            lot.expiry_date is None,
            lot.expiry_date or date.max,
            lot.created_at,
            lot.lot_id,
        ),
    )
    remaining = required_quantity
    allocations: list[StockAllocation] = []
    for lot in ordered:
        if remaining == 0:
            break
        quantity = min(lot.available_quantity, remaining)
        if quantity > 0:
            allocations.append(StockAllocation(lot.lot_id, quantity))
            remaining -= quantity
    return tuple(allocations)
