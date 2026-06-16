from datetime import date
from decimal import Decimal

import pytest

from gastroledger_api.modules.procurement.public import (
    CreateSupplier,
    CreateSupplierOffer,
    ProcurementAuthorizationDenied,
    ProcurementCodeConflict,
    ProcurementDateOverlap,
    ProcurementService,
    ProcurementValidationError,
    SupplierIdentity,
    validate_supplier,
    validate_supplier_offer,
)


def admin_identity() -> SupplierIdentity:
    return SupplierIdentity(
        tenant_id="tenant-1",
        actor_id="actor-1",
        role="tenant_admin",
    )


class RecordingSupplierStore:
    def __init__(self) -> None:
        self.suppliers: list[object] = []
        self.offers: list[object] = []
        self.overlap = False

    def list_suppliers(self, _identity: SupplierIdentity) -> tuple[object, ...]:
        return tuple(self.suppliers)

    def create_supplier(
        self,
        _identity: SupplierIdentity,
        supplier: object,
        _correlation_id: str,
    ) -> object:
        self.suppliers.append(supplier)
        return supplier

    def list_offers(self, _identity: SupplierIdentity) -> tuple[object, ...]:
        return tuple(self.offers)

    def create_supplier_offer(
        self,
        _identity: SupplierIdentity,
        offer: object,
        _correlation_id: str,
    ) -> object:
        if self.overlap:
            raise ProcurementDateOverlap
        self.offers.append(offer)
        return offer


def test_supplier_and_offer_inputs_are_normalized() -> None:
    supplier = validate_supplier(name="  North Market  ", code=" north-market ")
    offer = validate_supplier_offer(
        supplier_id=" supplier-1 ",
        ingredient_id=" ingredient-1 ",
        purchase_unit_id=" unit-1 ",
        price="12.500",
        currency=" usd ",
        effective_from=date(2026, 6, 16),
        effective_until=None,
    )

    assert (supplier.name, supplier.code) == ("North Market", "NORTH-MARKET")
    assert offer.price == Decimal("12.500")
    assert offer.currency == "USD"


def test_invalid_supplier_offer_dates_and_price_are_rejected() -> None:
    with pytest.raises(ProcurementValidationError) as error:
        validate_supplier_offer(
            supplier_id="supplier-1",
            ingredient_id="ingredient-1",
            purchase_unit_id="unit-1",
            price="0",
            currency="usd",
            effective_from=date(2026, 6, 16),
            effective_until=date(2026, 6, 15),
        )

    assert [(detail.field, detail.code) for detail in error.value.details] == [
        ("price", "positive_required"),
        ("effectiveUntil", "before_effective_from"),
    ]


def test_tenant_admin_records_suppliers_and_rejects_overlapping_offers() -> None:
    store = RecordingSupplierStore()
    service = ProcurementService(store=store)

    supplier = service.create_supplier(
        admin_identity(),
        CreateSupplier(name="North Market", code="north"),
        correlation_id="supplier-1",
    )
    offer = service.create_supplier_offer(
        admin_identity(),
        CreateSupplierOffer(
            supplier_id="supplier-1",
            ingredient_id="ingredient-1",
            purchase_unit_id="unit-1",
            price="12.50",
            currency="USD",
            effective_from=date(2026, 6, 16),
            effective_until=None,
        ),
        correlation_id="offer-1",
    )
    store.overlap = True

    with pytest.raises(ProcurementDateOverlap):
        service.create_supplier_offer(
            admin_identity(),
            CreateSupplierOffer(
                supplier_id="supplier-1",
                ingredient_id="ingredient-1",
                purchase_unit_id="unit-1",
                price="13.50",
                currency="USD",
                effective_from=date(2026, 6, 17),
                effective_until=None,
            ),
            correlation_id="offer-overlap",
        )

    assert getattr(supplier, "code") == "NORTH"
    assert getattr(offer, "price") == Decimal("12.50")


def test_non_admin_actor_cannot_mutate_suppliers() -> None:
    service = ProcurementService(store=RecordingSupplierStore())

    with pytest.raises(ProcurementAuthorizationDenied):
        service.create_supplier(
            SupplierIdentity(tenant_id="tenant-1", actor_id="actor-1", role="branch_operator"),
            CreateSupplier(name="North Market", code="NORTH"),
            correlation_id="supplier-1",
        )


def test_duplicate_supplier_code_is_visible_conflict() -> None:
    class ConflictStore(RecordingSupplierStore):
        def create_supplier(self, *_args: object, **_kwargs: object) -> object:
            raise ProcurementCodeConflict

    with pytest.raises(ProcurementCodeConflict):
        ProcurementService(store=ConflictStore()).create_supplier(
            admin_identity(),
            CreateSupplier(name="North Market", code="NORTH"),
            correlation_id="supplier-1",
        )
