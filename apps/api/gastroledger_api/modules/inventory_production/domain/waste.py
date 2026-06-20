from dataclasses import dataclass
from decimal import Decimal, InvalidOperation

HIGH_VALUE_THRESHOLD = Decimal("100")


@dataclass(frozen=True)
class WasteValidationDetail:
    field: str
    code: str


class WasteValidationError(Exception):
    def __init__(self, details: tuple[WasteValidationDetail, ...]) -> None:
        super().__init__("invalid waste")
        self.details = details


@dataclass(frozen=True)
class ValidatedWasteSubmission:
    lot_id: str
    quantity: Decimal
    reason: str


@dataclass(frozen=True)
class WasteState:
    status: str
    requested_by: str


def validate_waste_submission(
    *, lot_id: str, quantity: str, reason: str
) -> ValidatedWasteSubmission:
    details: list[WasteValidationDetail] = []
    try:
        parsed = Decimal(quantity)
    except (InvalidOperation, ValueError):
        parsed = Decimal("0")
        details.append(WasteValidationDetail("quantity", "invalid"))
    if not parsed.is_finite() or parsed <= 0:
        details.append(WasteValidationDetail("quantity", "must_be_positive"))
    if not lot_id.strip():
        details.append(WasteValidationDetail("lotId", "required"))
    if not reason.strip():
        details.append(WasteValidationDetail("reason", "required"))
    if details:
        raise WasteValidationError(tuple(details))
    return ValidatedWasteSubmission(lot_id.strip(), parsed, reason.strip())


def classify_waste(quantity: Decimal, unit_cost: Decimal) -> str:
    return (
        "pending_approval" if quantity * unit_cost >= HIGH_VALUE_THRESHOLD else "post_immediately"
    )


def approve_waste(state: WasteState, approver_id: str) -> WasteState:
    if state.status != "pending_approval" or state.requested_by == approver_id:
        raise WasteValidationError(
            (WasteValidationDetail("approval", "separate_approver_required"),)
        )
    return WasteState("approved", state.requested_by)
