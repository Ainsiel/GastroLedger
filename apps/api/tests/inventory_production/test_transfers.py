from decimal import Decimal

import pytest

from gastroledger_api.modules.inventory_production.domain.transfers import (
    TransferState,
    TransferValidationError,
    approve_transfer,
    dispatch_transfer,
    receive_transfer,
    validate_transfer_request,
)


def test_request_requires_different_warehouses() -> None:
    with pytest.raises(TransferValidationError) as error:
        validate_transfer_request(
            transfer_number="TR-001",
            source_warehouse_id="same",
            destination_warehouse_id="same",
            item_type="ingredient",
            item_id="item",
            unit_id="unit",
            requested_quantity="5",
        )
    assert error.value.details[0].code == "warehouses_must_differ"


def test_approval_preserves_requested_and_may_reduce_quantity() -> None:
    state = TransferState(
        "requested", Decimal("10"), Decimal("0"), Decimal("0"), Decimal("0"), Decimal("0")
    )
    approved = approve_transfer(state, Decimal("7"))
    assert approved.requested_quantity == Decimal("10")
    assert approved.approved_quantity == Decimal("7")
    with pytest.raises(TransferValidationError):
        approve_transfer(state, Decimal("11"))


def test_dispatch_and_receipt_totals_are_monotonic() -> None:
    approved = TransferState(
        "approved", Decimal("10"), Decimal("8"), Decimal("0"), Decimal("0"), Decimal("0")
    )
    partial = dispatch_transfer(approved, Decimal("5"))
    assert partial.status == "partially_dispatched"
    received = receive_transfer(partial, Decimal("4"), Decimal("1"), "transport damage")
    assert received.status == "partially_dispatched"
    with pytest.raises(TransferValidationError):
        receive_transfer(partial, Decimal("5"), Decimal("1"), "too much")
