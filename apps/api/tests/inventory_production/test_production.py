from datetime import UTC, date, datetime
from decimal import Decimal

import pytest

from gastroledger_api.modules.inventory_production.domain.production import (
    ProductionValidationError,
    StockLot,
    allocate_stock,
    validate_production_batch,
)


def test_allocation_uses_fefo_then_fifo_for_lots_without_expiry() -> None:
    lots = (
        StockLot("fifo-old", Decimal("4"), None, datetime(2026, 1, 1, tzinfo=UTC)),
        StockLot(
            "later", Decimal("5"), date(2026, 8, 1), datetime(2026, 1, 2, tzinfo=UTC)
        ),
        StockLot(
            "sooner", Decimal("3"), date(2026, 7, 1), datetime(2026, 1, 3, tzinfo=UTC)
        ),
    )

    allocations = allocate_stock(lots, Decimal("10"))

    assert [(item.lot_id, item.quantity) for item in allocations] == [
        ("sooner", Decimal("3")),
        ("later", Decimal("5")),
        ("fifo-old", Decimal("2")),
    ]


def test_lower_actual_yield_requires_variance_reason() -> None:
    with pytest.raises(ProductionValidationError) as error:
        validate_production_batch(
            idempotency_key="batch-001",
            batch_number="B-001",
            warehouse_id="warehouse",
            recipe_version_id="recipe-version",
            actual_yield="8",
            output_lot_code="PREP-001",
            produced_on=date(2026, 6, 20),
            variance_reason="",
            expected_yield=Decimal("10"),
        )

    assert ("varianceReason", "required_for_lower_yield") in {
        (detail.field, detail.code) for detail in error.value.details
    }


def test_insufficient_stock_rejects_allocation() -> None:
    with pytest.raises(ProductionValidationError) as error:
        allocate_stock(
            (StockLot("only", Decimal("2"), None, datetime.now(UTC)),),
            Decimal("3"),
        )

    assert error.value.details[0].code == "insufficient_stock"
