from datetime import date
from decimal import Decimal

import pytest

from gastroledger_api.modules.procurement.public import (
    CreateSupplierReceipt,
    CreateSupplierReceiptLine,
    ProcurementAuthorizationDenied,
    ProcurementReceiptService,
    SupplierIdentity,
    validate_supplier_receipt,
)


def test_receipt_validation_classifies_partial_and_rejected_lines() -> None:
    receipt = validate_supplier_receipt(
        idempotency_key=" receive-001 ",
        order_reference=" po-seeded-1 ",
        supplier_id="supplier-1",
        warehouse_id="warehouse-1",
        received_on=date(2026, 6, 19),
        lines=(
            CreateSupplierReceiptLine(
                ingredient_id="ingredient-1",
                purchase_unit_id="unit-1",
                lot_code="lot-1",
                ordered_quantity="10",
                delivered_quantity="6",
                unit_cost="2.50",
                expiry_date=date(2026, 7, 19),
                temperature="4",
                minimum_temperature="1",
                maximum_temperature="6",
                tolerance_percent="5",
            ),
            CreateSupplierReceiptLine(
                ingredient_id="ingredient-2",
                purchase_unit_id="unit-1",
                lot_code="lot-hot",
                ordered_quantity="5",
                delivered_quantity="5",
                unit_cost="3",
                expiry_date=date(2026, 7, 19),
                temperature="12",
                minimum_temperature="1",
                maximum_temperature="6",
                tolerance_percent="0",
            ),
        ),
    )

    assert receipt.idempotency_key == "receive-001"
    assert receipt.lines[0].status == "partial"
    assert receipt.lines[0].accepted_quantity == Decimal("6")
    assert receipt.lines[0].remaining_quantity == Decimal("4")
    assert receipt.lines[1].status == "rejected"
    assert receipt.lines[1].rejection_reason == "temperature_out_of_range"


class RecordingReceiptStore:
    def __init__(self) -> None:
        self.receipts: list[object] = []

    def accept_supplier_receipt(self, _identity, receipt, _correlation_id):
        self.receipts.append(receipt)
        return {"receipt_id": "receipt-1", "status": "accepted"}


def test_receipt_service_requires_warehouse_actor_and_passes_validated_command() -> None:
    store = RecordingReceiptStore()
    service = ProcurementReceiptService(store=store)
    command = CreateSupplierReceipt(
        idempotency_key="receive-001",
        order_reference="po-1",
        supplier_id="supplier-1",
        warehouse_id="warehouse-1",
        received_on=date(2026, 6, 19),
        lines=(
            CreateSupplierReceiptLine(
                "ingredient-1",
                "unit-1",
                "lot-1",
                "1",
                "1",
                "2",
                date(2026, 7, 19),
                "4",
                "1",
                "6",
                "0",
            ),
        ),
    )

    result = service.accept_supplier_receipt(
        SupplierIdentity("tenant-1", "actor-1", "tenant_admin"),
        command,
        correlation_id="receipt-correlation",
    )

    assert result["status"] == "accepted"
    assert store.receipts[0].lines[0].accepted_quantity == Decimal("1")

    with pytest.raises(ProcurementAuthorizationDenied):
        service.accept_supplier_receipt(
            SupplierIdentity("tenant-1", "actor-2", "tenant_operator"),
            command,
            correlation_id="denied",
        )
