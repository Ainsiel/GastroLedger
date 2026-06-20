from dataclasses import dataclass, replace
from decimal import Decimal, InvalidOperation


@dataclass(frozen=True)
class TransferValidationDetail:
    field: str
    code: str


class TransferValidationError(Exception):
    def __init__(self, details: tuple[TransferValidationDetail, ...]) -> None:
        super().__init__("invalid transfer")
        self.details = details


@dataclass(frozen=True)
class ValidatedTransferRequest:
    transfer_number: str
    source_warehouse_id: str
    destination_warehouse_id: str
    item_type: str
    item_id: str
    unit_id: str
    requested_quantity: Decimal


@dataclass(frozen=True)
class TransferState:
    status: str
    requested_quantity: Decimal
    approved_quantity: Decimal
    dispatched_quantity: Decimal
    received_quantity: Decimal
    loss_quantity: Decimal


def _positive(value: str, field: str) -> Decimal:
    try:
        parsed = Decimal(value)
    except (InvalidOperation, ValueError) as error:
        raise TransferValidationError((TransferValidationDetail(field, "invalid"),)) from error
    if not parsed.is_finite() or parsed <= 0:
        raise TransferValidationError((TransferValidationDetail(field, "must_be_positive"),))
    return parsed


def validate_transfer_request(
    *,
    transfer_number: str,
    source_warehouse_id: str,
    destination_warehouse_id: str,
    item_type: str,
    item_id: str,
    unit_id: str,
    requested_quantity: str,
) -> ValidatedTransferRequest:
    if source_warehouse_id.strip() == destination_warehouse_id.strip():
        raise TransferValidationError(
            (TransferValidationDetail("destinationWarehouseId", "warehouses_must_differ"),)
        )
    values = [transfer_number, source_warehouse_id, destination_warehouse_id, item_id, unit_id]
    if any(not value.strip() for value in values) or item_type not in {
        "ingredient",
        "prepared_recipe",
    }:
        raise TransferValidationError((TransferValidationDetail("transfer", "invalid"),))
    return ValidatedTransferRequest(
        transfer_number.strip().upper(),
        source_warehouse_id.strip(),
        destination_warehouse_id.strip(),
        item_type,
        item_id.strip(),
        unit_id.strip(),
        _positive(requested_quantity, "requestedQuantity"),
    )


def approve_transfer(state: TransferState, quantity: Decimal) -> TransferState:
    if state.status != "requested" or quantity <= 0 or quantity > state.requested_quantity:
        raise TransferValidationError((TransferValidationDetail("approvedQuantity", "invalid"),))
    return replace(state, status="approved", approved_quantity=quantity)


def dispatch_transfer(state: TransferState, quantity: Decimal) -> TransferState:
    remaining = state.approved_quantity - state.dispatched_quantity
    if (
        state.status not in {"approved", "partially_dispatched", "partially_received"}
        or quantity <= 0
        or quantity > remaining
    ):
        raise TransferValidationError((TransferValidationDetail("dispatchQuantity", "invalid"),))
    dispatched = state.dispatched_quantity + quantity
    status = (
        "dispatched"
        if dispatched == state.approved_quantity
        and state.received_quantity + state.loss_quantity == 0
        else "partially_dispatched"
    )
    return replace(state, status=status, dispatched_quantity=dispatched)


def receive_transfer(
    state: TransferState, received: Decimal, loss: Decimal, loss_reason: str
) -> TransferState:
    if received < 0 or loss < 0 or (loss > 0 and not loss_reason.strip()):
        raise TransferValidationError((TransferValidationDetail("receipt", "invalid"),))
    remaining = state.dispatched_quantity - state.received_quantity - state.loss_quantity
    if (
        state.status not in {"dispatched", "partially_dispatched", "partially_received"}
        or received + loss <= 0
        or received + loss > remaining
    ):
        raise TransferValidationError(
            (TransferValidationDetail("receiptQuantity", "exceeds_dispatched"),)
        )
    received_total = state.received_quantity + received
    loss_total = state.loss_quantity + loss
    reconciled = received_total + loss_total
    status = (
        "completed"
        if reconciled == state.dispatched_quantity == state.approved_quantity
        else "partially_dispatched"
        if reconciled == state.dispatched_quantity
        else "partially_received"
    )
    return replace(state, status=status, received_quantity=received_total, loss_quantity=loss_total)
