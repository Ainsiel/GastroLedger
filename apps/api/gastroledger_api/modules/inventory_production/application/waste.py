from dataclasses import dataclass
from decimal import Decimal
from typing import Protocol

from gastroledger_api.modules.inventory_production.domain.waste import (
    ValidatedWasteSubmission,
    validate_waste_submission,
)


class WasteAuthorizationDenied(Exception):
    pass


class WasteNotFound(Exception):
    pass


class WasteConflict(Exception):
    pass


class WasteInsufficientStock(Exception):
    pass


@dataclass(frozen=True)
class WasteIdentity:
    tenant_id: str
    actor_id: str
    role: str


@dataclass(frozen=True)
class SubmitWaste:
    command_key: str
    warehouse_id: str
    lot_id: str
    quantity: str
    reason: str


@dataclass(frozen=True)
class WasteView:
    waste_id: str
    status: str
    warehouse_id: str
    lot_id: str
    quantity: Decimal
    operational_value: Decimal
    reason: str
    requested_by: str
    decision_by: str | None
    inventory_transaction_id: str | None


class WasteStore(Protocol):
    def submit_waste(
        self,
        identity: WasteIdentity,
        command_key: str,
        warehouse_id: str,
        waste: ValidatedWasteSubmission,
        correlation_id: str,
    ) -> WasteView: ...
    def approve_waste(
        self, identity: WasteIdentity, waste_id: str, command_key: str, correlation_id: str
    ) -> WasteView: ...
    def reject_waste(
        self, identity: WasteIdentity, waste_id: str, reason: str, correlation_id: str
    ) -> WasteView: ...
    def correct_waste(
        self,
        identity: WasteIdentity,
        waste_id: str,
        command_key: str,
        reason: str,
        correlation_id: str,
    ) -> WasteView: ...


class WasteService:
    def __init__(self, *, store: WasteStore) -> None:
        self._store = store

    def submit_waste(
        self, identity: WasteIdentity, command: SubmitWaste, *, correlation_id: str
    ) -> WasteView:
        self._authorize(identity)
        waste = validate_waste_submission(
            lot_id=command.lot_id, quantity=command.quantity, reason=command.reason
        )
        return self._store.submit_waste(
            identity,
            command.command_key.strip(),
            command.warehouse_id.strip(),
            waste,
            correlation_id,
        )

    def approve_waste(
        self, identity: WasteIdentity, waste_id: str, command_key: str, *, correlation_id: str
    ) -> WasteView:
        self._authorize(identity, True)
        return self._store.approve_waste(identity, waste_id, command_key.strip(), correlation_id)

    def reject_waste(
        self, identity: WasteIdentity, waste_id: str, reason: str, *, correlation_id: str
    ) -> WasteView:
        self._authorize(identity, True)
        return self._store.reject_waste(identity, waste_id, reason.strip(), correlation_id)

    def correct_waste(
        self,
        identity: WasteIdentity,
        waste_id: str,
        command_key: str,
        reason: str,
        *,
        correlation_id: str,
    ) -> WasteView:
        self._authorize(identity, True)
        return self._store.correct_waste(
            identity, waste_id, command_key.strip(), reason.strip(), correlation_id
        )

    @staticmethod
    def _authorize(identity: WasteIdentity, manager: bool = False) -> None:
        roles = (
            {"tenant_admin", "branch_manager"}
            if manager
            else {"tenant_admin", "branch_manager", "branch_operator"}
        )
        if identity.role not in roles:
            raise WasteAuthorizationDenied
