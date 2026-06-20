from decimal import Decimal

import pytest

from gastroledger_api.modules.inventory_production.domain.waste import (
    WasteState,
    WasteValidationError,
    approve_waste,
    classify_waste,
    validate_waste_submission,
)


def test_waste_requires_reason_and_positive_quantity() -> None:
    with pytest.raises(WasteValidationError):
        validate_waste_submission(lot_id="lot", quantity="1", reason="")
    with pytest.raises(WasteValidationError):
        validate_waste_submission(lot_id="lot", quantity="0", reason="spoilage")


def test_high_value_waste_requires_approval() -> None:
    assert classify_waste(Decimal("4"), Decimal("24")) == "post_immediately"
    assert classify_waste(Decimal("4"), Decimal("25")) == "pending_approval"


def test_requester_cannot_approve_own_waste() -> None:
    state = WasteState("pending_approval", "operator-1")
    with pytest.raises(WasteValidationError):
        approve_waste(state, "operator-1")
    assert approve_waste(state, "manager-1").status == "approved"
