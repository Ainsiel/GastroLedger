from dataclasses import dataclass
from decimal import Decimal
from typing import Protocol

from gastroledger_api.modules.inventory_production.domain.transfers import (
    ValidatedTransferRequest,
    validate_transfer_request,
)


class TransferAuthorizationDenied(Exception):
    pass


class TransferNotFound(Exception):
    pass


class TransferConflict(Exception):
    pass


class TransferInsufficientStock(Exception):
    pass


@dataclass(frozen=True)
class TransferIdentity:
    tenant_id: str
    actor_id: str
    role: str


@dataclass(frozen=True)
class RequestTransfer:
    transfer_number: str
    source_warehouse_id: str
    destination_warehouse_id: str
    item_type: str
    item_id: str
    unit_id: str
    requested_quantity: str


@dataclass(frozen=True)
class TransferView:
    transfer_id: str
    transfer_number: str
    status: str
    source_warehouse_id: str
    destination_warehouse_id: str
    item_type: str
    item_id: str
    unit_id: str
    requested_quantity: Decimal
    approved_quantity: Decimal
    dispatched_quantity: Decimal
    received_quantity: Decimal
    loss_quantity: Decimal


class TransferStore(Protocol):
    def request_transfer(
        self, identity: TransferIdentity, transfer: ValidatedTransferRequest, correlation_id: str
    ) -> TransferView: ...
    def approve_transfer(
        self, identity: TransferIdentity, transfer_id: str, quantity: Decimal, correlation_id: str
    ) -> TransferView: ...
    def dispatch_transfer(
        self,
        identity: TransferIdentity,
        transfer_id: str,
        command_key: str,
        quantity: Decimal,
        correlation_id: str,
    ) -> TransferView: ...
    def receive_transfer(
        self,
        identity: TransferIdentity,
        transfer_id: str,
        command_key: str,
        received: Decimal,
        loss: Decimal,
        reason: str,
        correlation_id: str,
    ) -> TransferView: ...


class TransferService:
    def __init__(self, *, store: TransferStore) -> None:
        self._store = store

    def request_transfer(
        self, identity: TransferIdentity, command: RequestTransfer, *, correlation_id: str
    ) -> TransferView:
        self._authorize(identity, manager=True)
        return self._store.request_transfer(
            identity,
            validate_transfer_request(
                transfer_number=command.transfer_number,
                source_warehouse_id=command.source_warehouse_id,
                destination_warehouse_id=command.destination_warehouse_id,
                item_type=command.item_type,
                item_id=command.item_id,
                unit_id=command.unit_id,
                requested_quantity=command.requested_quantity,
            ),
            correlation_id,
        )

    def approve_transfer(
        self, identity: TransferIdentity, transfer_id: str, quantity: str, *, correlation_id: str
    ) -> TransferView:
        self._authorize(identity, manager=True)
        return self._store.approve_transfer(
            identity, transfer_id, Decimal(quantity), correlation_id
        )

    def dispatch_transfer(
        self,
        identity: TransferIdentity,
        transfer_id: str,
        command_key: str,
        quantity: str,
        *,
        correlation_id: str,
    ) -> TransferView:
        self._authorize(identity)
        return self._store.dispatch_transfer(
            identity, transfer_id, command_key.strip(), Decimal(quantity), correlation_id
        )

    def receive_transfer(
        self,
        identity: TransferIdentity,
        transfer_id: str,
        command_key: str,
        received: str,
        loss: str,
        reason: str,
        *,
        correlation_id: str,
    ) -> TransferView:
        self._authorize(identity)
        return self._store.receive_transfer(
            identity,
            transfer_id,
            command_key.strip(),
            Decimal(received),
            Decimal(loss),
            reason,
            correlation_id,
        )

    @staticmethod
    def _authorize(identity: TransferIdentity, manager: bool = False) -> None:
        roles = (
            {"tenant_admin", "branch_manager"}
            if manager
            else {"tenant_admin", "branch_manager", "branch_operator"}
        )
        if identity.role not in roles:
            raise TransferAuthorizationDenied
