from dataclasses import dataclass
from datetime import date, datetime
from typing import Protocol


class ExpiryAlertAuthorizationDenied(PermissionError):
    pass


class ExpiryAlertNotFound(LookupError):
    pass


class ExpiryAlertConflict(RuntimeError):
    pass


class ExpiryAlertInvalid(ValueError):
    pass


@dataclass(frozen=True)
class ExpiryAlertIdentity:
    tenant_id: str
    actor_id: str
    role: str


@dataclass(frozen=True)
class ExpiryAlertView:
    alert_id: str
    warehouse_id: str
    lot_id: str
    lot_code: str
    expiry_date: date
    status: str
    rule_key: str
    created_at: datetime
    acknowledged_by: str | None
    acknowledged_at: datetime | None
    action_note: str | None


class ExpiryAlertStore(Protocol):
    def list_expiry_alerts(
        self, identity: ExpiryAlertIdentity, status: str
    ) -> tuple[ExpiryAlertView, ...]: ...

    def acknowledge_expiry_alert(
        self,
        identity: ExpiryAlertIdentity,
        alert_id: str,
        action_note: str,
        correlation_id: str,
    ) -> ExpiryAlertView: ...


class ExpiryAlertService:
    def __init__(self, *, store: ExpiryAlertStore) -> None:
        self._store = store

    def list_alerts(
        self, identity: ExpiryAlertIdentity, status: str
    ) -> tuple[ExpiryAlertView, ...]:
        self._authorize(identity)
        if status not in {"active", "acknowledged"}:
            raise ExpiryAlertInvalid
        return self._store.list_expiry_alerts(identity, status)

    def acknowledge(
        self,
        identity: ExpiryAlertIdentity,
        alert_id: str,
        action_note: str,
        correlation_id: str,
    ) -> ExpiryAlertView:
        self._authorize(identity)
        if not action_note.strip():
            raise ExpiryAlertInvalid
        return self._store.acknowledge_expiry_alert(
            identity, alert_id, action_note.strip(), correlation_id
        )

    @staticmethod
    def _authorize(identity: ExpiryAlertIdentity) -> None:
        if identity.role not in {"tenant_admin", "branch_manager", "branch_operator"}:
            raise ExpiryAlertAuthorizationDenied
