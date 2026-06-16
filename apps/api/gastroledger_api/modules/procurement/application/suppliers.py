from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Protocol

from gastroledger_api.application.identifiers import ActorId, TenantId
from gastroledger_api.modules.procurement.domain.suppliers import (
    ValidatedSupplier,
    ValidatedSupplierOffer,
    validate_supplier,
    validate_supplier_offer,
)


@dataclass(frozen=True)
class SupplierIdentity:
    tenant_id: TenantId
    actor_id: ActorId
    role: str


@dataclass(frozen=True)
class CreateSupplier:
    name: str
    code: str


@dataclass(frozen=True)
class CreateSupplierOffer:
    supplier_id: str
    ingredient_id: str
    purchase_unit_id: str
    price: str
    currency: str
    effective_from: date
    effective_until: date | None


class ProcurementAuthorizationDenied(Exception):
    pass


class ProcurementCodeConflict(Exception):
    pass


class ProcurementNotFound(Exception):
    pass


class ProcurementDateOverlap(Exception):
    pass


class ProcurementUnitMismatch(Exception):
    pass


@dataclass(frozen=True)
class SupplierView:
    supplier_id: str
    name: str
    code: str
    status: str


@dataclass(frozen=True)
class SupplierOfferView:
    supplier_offer_id: str
    supplier_id: str
    ingredient_id: str
    purchase_unit_id: str
    price: Decimal
    currency: str
    effective_from: date
    effective_until: date | None


class ProcurementStore(Protocol):
    def list_suppliers(self, identity: SupplierIdentity) -> tuple[SupplierView, ...]: ...

    def create_supplier(
        self,
        identity: SupplierIdentity,
        supplier: ValidatedSupplier,
        correlation_id: str,
    ) -> SupplierView: ...

    def list_offers(self, identity: SupplierIdentity) -> tuple[SupplierOfferView, ...]: ...

    def create_supplier_offer(
        self,
        identity: SupplierIdentity,
        offer: ValidatedSupplierOffer,
        correlation_id: str,
    ) -> SupplierOfferView: ...


class ProcurementService:
    def __init__(self, *, store: ProcurementStore) -> None:
        self._store = store

    def list_suppliers(self, identity: SupplierIdentity) -> tuple[SupplierView, ...]:
        self._require_procurement_actor(identity)
        return self._store.list_suppliers(identity)

    def create_supplier(
        self,
        identity: SupplierIdentity,
        command: CreateSupplier,
        *,
        correlation_id: str,
    ) -> SupplierView:
        self._require_procurement_actor(identity)
        supplier = validate_supplier(name=command.name, code=command.code)
        return self._store.create_supplier(identity, supplier, correlation_id)

    def list_offers(self, identity: SupplierIdentity) -> tuple[SupplierOfferView, ...]:
        self._require_procurement_actor(identity)
        return self._store.list_offers(identity)

    def create_supplier_offer(
        self,
        identity: SupplierIdentity,
        command: CreateSupplierOffer,
        *,
        correlation_id: str,
    ) -> SupplierOfferView:
        self._require_procurement_actor(identity)
        offer = validate_supplier_offer(
            supplier_id=command.supplier_id,
            ingredient_id=command.ingredient_id,
            purchase_unit_id=command.purchase_unit_id,
            price=command.price,
            currency=command.currency,
            effective_from=command.effective_from,
            effective_until=command.effective_until,
        )
        return self._store.create_supplier_offer(identity, offer, correlation_id)

    @staticmethod
    def _require_procurement_actor(identity: SupplierIdentity) -> None:
        if identity.role != "tenant_admin":
            raise ProcurementAuthorizationDenied
