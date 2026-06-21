from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal

EXPIRY_ALERT_WINDOW_DAYS = 3
EXPIRY_ALERT_RULE_KEY = "expiry-within-3-days-v1"


class ExpiryAlertValidationError(ValueError):
    pass


@dataclass(frozen=True)
class ExpiryAlertState:
    status: str


def requires_expiry_alert(
    expiry_date: date | None, available_quantity: Decimal, as_of: date
) -> bool:
    return (
        expiry_date is not None
        and available_quantity > 0
        and expiry_date <= as_of + timedelta(days=EXPIRY_ALERT_WINDOW_DAYS)
    )


def acknowledge_alert(state: ExpiryAlertState, action_note: str) -> tuple[str, str]:
    normalized_note = action_note.strip()
    if state.status != "active" or not normalized_note:
        raise ExpiryAlertValidationError
    return "acknowledged", normalized_note
