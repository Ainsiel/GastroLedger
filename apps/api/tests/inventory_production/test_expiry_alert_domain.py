from datetime import date
from decimal import Decimal

import pytest

from gastroledger_api.modules.inventory_production.domain.expiry_alerts import (
    ExpiryAlertState,
    ExpiryAlertValidationError,
    acknowledge_alert,
    requires_expiry_alert,
)


def test_alert_is_required_for_stock_expiring_within_three_days() -> None:
    as_of = date(2026, 6, 21)

    assert requires_expiry_alert(date(2026, 6, 24), Decimal("1"), as_of)
    assert requires_expiry_alert(date(2026, 6, 20), Decimal("1"), as_of)
    assert not requires_expiry_alert(date(2026, 6, 25), Decimal("1"), as_of)


def test_alert_is_not_required_without_expiry_or_positive_stock() -> None:
    as_of = date(2026, 6, 21)

    assert not requires_expiry_alert(None, Decimal("1"), as_of)
    assert not requires_expiry_alert(date(2026, 6, 22), Decimal("0"), as_of)


def test_acknowledgement_requires_active_alert_and_action_note() -> None:
    with pytest.raises(ExpiryAlertValidationError):
        acknowledge_alert(ExpiryAlertState("active"), "  ")
    with pytest.raises(ExpiryAlertValidationError):
        acknowledge_alert(ExpiryAlertState("acknowledged"), "Moved to prep")

    assert acknowledge_alert(ExpiryAlertState("active"), " Moved to prep ") == (
        "acknowledged",
        "Moved to prep",
    )
