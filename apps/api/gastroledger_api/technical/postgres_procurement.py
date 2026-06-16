from datetime import UTC, date, datetime
from uuid import UUID, uuid4

from psycopg import errors
from sqlalchemy import create_engine, or_, select, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy.pool import NullPool

from gastroledger_api.modules.procurement.application.suppliers import (
    ProcurementAuthorizationDenied,
    ProcurementCodeConflict,
    ProcurementDateOverlap,
    ProcurementNotFound,
    ProcurementUnitMismatch,
    SupplierIdentity,
    SupplierOfferView,
    SupplierView,
)
from gastroledger_api.modules.procurement.domain.suppliers import (
    ValidatedSupplier,
    ValidatedSupplierOffer,
)
from gastroledger_api.technical.menu_models import MenuIngredient
from gastroledger_api.technical.platform_models import ControlAuditEvent, PlatformMembership
from gastroledger_api.technical.postgres_platform import sqlalchemy_database_url
from gastroledger_api.technical.procurement_models import (
    ProcurementSupplier,
    ProcurementSupplierOffer,
)


class PostgresProcurementStore:
    def __init__(self, database_url: str) -> None:
        self._database_url = database_url
        self._engine: Engine | None = None

    def _open_session(self) -> Session:
        if self._engine is None:
            self._engine = create_engine(
                sqlalchemy_database_url(self._database_url), poolclass=NullPool
            )
        return Session(self._engine)

    def list_suppliers(self, identity: SupplierIdentity) -> tuple[SupplierView, ...]:
        with self._open_session() as session, session.begin():
            self._authorize_procurement_identity(session, identity)
            suppliers = session.execute(
                select(ProcurementSupplier)
                .where(ProcurementSupplier.tenant_id == UUID(identity.tenant_id))
                .order_by(ProcurementSupplier.code)
            ).scalars()
            return tuple(self._supplier_view(supplier) for supplier in suppliers)

    def create_supplier(
        self,
        identity: SupplierIdentity,
        supplier: ValidatedSupplier,
        correlation_id: str,
    ) -> SupplierView:
        supplier_uuid = uuid4()
        try:
            with self._open_session() as session, session.begin():
                self._authorize_procurement_identity(session, identity)
                record = ProcurementSupplier(
                    id=supplier_uuid,
                    tenant_id=UUID(identity.tenant_id),
                    code=supplier.code,
                    name=supplier.name,
                    status="active",
                )
                session.add(record)
                session.flush()
                self._audit(
                    session,
                    identity,
                    correlation_id,
                    "procurement.supplier.created",
                    str(supplier_uuid),
                )
                return self._supplier_view(record)
        except IntegrityError as error:
            if isinstance(error.orig, errors.UniqueViolation):
                raise ProcurementCodeConflict from error
            raise

    def list_offers(self, identity: SupplierIdentity) -> tuple[SupplierOfferView, ...]:
        with self._open_session() as session, session.begin():
            self._authorize_procurement_identity(session, identity)
            offers = session.execute(
                select(ProcurementSupplierOffer)
                .where(ProcurementSupplierOffer.tenant_id == UUID(identity.tenant_id))
                .order_by(
                    ProcurementSupplierOffer.effective_from,
                    ProcurementSupplierOffer.id,
                )
            ).scalars()
            return tuple(self._offer_view(offer) for offer in offers)

    def create_supplier_offer(
        self,
        identity: SupplierIdentity,
        offer: ValidatedSupplierOffer,
        correlation_id: str,
    ) -> SupplierOfferView:
        offer_uuid = uuid4()
        try:
            with self._open_session() as session, session.begin():
                self._authorize_procurement_identity(session, identity)
                self._ensure_supplier(session, identity, offer.supplier_id)
                self._ensure_ingredient_unit(
                    session,
                    identity,
                    offer.ingredient_id,
                    offer.purchase_unit_id,
                )
                if self._overlapping_offer_exists(session, identity, offer):
                    raise ProcurementDateOverlap
                record = ProcurementSupplierOffer(
                    id=offer_uuid,
                    tenant_id=UUID(identity.tenant_id),
                    supplier_id=UUID(offer.supplier_id),
                    ingredient_id=UUID(offer.ingredient_id),
                    purchase_unit_id=UUID(offer.purchase_unit_id),
                    price=offer.price,
                    currency=offer.currency,
                    effective_from=offer.effective_from,
                    effective_until=offer.effective_until,
                )
                session.add(record)
                session.flush()
                self._audit(
                    session,
                    identity,
                    correlation_id,
                    "procurement.offer.created",
                    str(offer_uuid),
                )
                return self._offer_view(record)
        except IntegrityError as error:
            if isinstance(error.orig, errors.UniqueViolation):
                raise ProcurementCodeConflict from error
            raise

    @staticmethod
    def _authorize_procurement_identity(session: Session, identity: SupplierIdentity) -> None:
        session.execute(text("set local role gastroledger_app"))
        session.execute(
            text("select set_config('app.current_tenant_id', :tenant_id, true)"),
            {"tenant_id": str(identity.tenant_id)},
        )
        role = session.execute(
            select(PlatformMembership.role).where(
                PlatformMembership.tenant_id == UUID(identity.tenant_id),
                PlatformMembership.user_id == UUID(identity.actor_id),
            )
        ).scalar_one_or_none()
        if role != "tenant_admin":
            raise ProcurementAuthorizationDenied

    @staticmethod
    def _ensure_supplier(
        session: Session,
        identity: SupplierIdentity,
        supplier_id: str,
    ) -> ProcurementSupplier:
        supplier = session.execute(
            select(ProcurementSupplier).where(
                ProcurementSupplier.tenant_id == UUID(identity.tenant_id),
                ProcurementSupplier.id == UUID(supplier_id),
                ProcurementSupplier.status == "active",
            )
        ).scalar_one_or_none()
        if supplier is None:
            raise ProcurementNotFound
        return supplier

    @staticmethod
    def _ensure_ingredient_unit(
        session: Session,
        identity: SupplierIdentity,
        ingredient_id: str,
        purchase_unit_id: str,
    ) -> None:
        ingredient = session.execute(
            select(MenuIngredient).where(
                MenuIngredient.tenant_id == UUID(identity.tenant_id),
                MenuIngredient.id == UUID(ingredient_id),
                MenuIngredient.status == "active",
            )
        ).scalar_one_or_none()
        if ingredient is None:
            raise ProcurementNotFound
        if ingredient.purchase_unit_id != UUID(purchase_unit_id):
            raise ProcurementUnitMismatch

    @staticmethod
    def _overlapping_offer_exists(
        session: Session,
        identity: SupplierIdentity,
        offer: ValidatedSupplierOffer,
    ) -> bool:
        existing = session.execute(
            select(ProcurementSupplierOffer.id)
            .where(
                ProcurementSupplierOffer.tenant_id == UUID(identity.tenant_id),
                ProcurementSupplierOffer.supplier_id == UUID(offer.supplier_id),
                ProcurementSupplierOffer.ingredient_id == UUID(offer.ingredient_id),
                ProcurementSupplierOffer.purchase_unit_id == UUID(offer.purchase_unit_id),
                ProcurementSupplierOffer.effective_from
                <= (offer.effective_until or date(9999, 12, 31)),
                or_(
                    ProcurementSupplierOffer.effective_until.is_(None),
                    ProcurementSupplierOffer.effective_until >= offer.effective_from,
                ),
            )
            .limit(1)
        ).scalar_one_or_none()
        return existing is not None

    @staticmethod
    def _audit(
        session: Session,
        identity: SupplierIdentity,
        correlation_id: str,
        action: str,
        object_reference: str,
    ) -> None:
        session.add(
            ControlAuditEvent(
                id=uuid4(),
                tenant_id=UUID(identity.tenant_id),
                actor_id=UUID(identity.actor_id),
                correlation_id=correlation_id,
                action=action,
                object_reference=object_reference,
                occurred_at=datetime.now(UTC),
            )
        )

    @staticmethod
    def _supplier_view(supplier: ProcurementSupplier) -> SupplierView:
        return SupplierView(
            supplier_id=str(supplier.id),
            name=supplier.name,
            code=supplier.code,
            status=supplier.status,
        )

    @staticmethod
    def _offer_view(offer: ProcurementSupplierOffer) -> SupplierOfferView:
        return SupplierOfferView(
            supplier_offer_id=str(offer.id),
            supplier_id=str(offer.supplier_id),
            ingredient_id=str(offer.ingredient_id),
            purchase_unit_id=str(offer.purchase_unit_id),
            price=offer.price,
            currency=offer.currency,
            effective_from=offer.effective_from,
            effective_until=offer.effective_until,
        )
