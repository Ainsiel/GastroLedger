from datetime import UTC, date, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from psycopg import errors
from sqlalchemy import create_engine, or_, select, text
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.engine import Engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy.pool import NullPool

from gastroledger_api.modules.procurement.application.receipts import (
    SupplierReceiptLineView,
    SupplierReceiptView,
)
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
from gastroledger_api.modules.procurement.domain.receipts import ValidatedSupplierReceipt
from gastroledger_api.modules.procurement.domain.suppliers import (
    ValidatedSupplier,
    ValidatedSupplierOffer,
)
from gastroledger_api.technical.cost_projection_models import (
    ControlJob,
    ControlOutboxEvent,
    MenuCostProjectionState,
)
from gastroledger_api.technical.inventory_models import (
    InventoryEntry,
    InventoryLot,
    InventoryStockBalance,
    InventoryTransaction,
)
from gastroledger_api.technical.menu_models import (
    MenuIngredient,
    MenuRecipeComponent,
    MenuRecipeVersion,
)
from gastroledger_api.technical.platform_models import (
    ControlAuditEvent,
    PlatformMembership,
    PlatformWarehouse,
)
from gastroledger_api.technical.postgres_platform import sqlalchemy_database_url
from gastroledger_api.technical.procurement_models import (
    ProcurementSupplier,
    ProcurementSupplierOffer,
    ProcurementSupplierReceipt,
    ProcurementSupplierReceiptLine,
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
                self._enqueue_cost_recalculation(
                    session,
                    identity,
                    ingredient_id=record.ingredient_id,
                    offer_id=record.id,
                    correlation_id=correlation_id,
                )
                return self._offer_view(record)
        except IntegrityError as error:
            if isinstance(error.orig, errors.UniqueViolation):
                raise ProcurementCodeConflict from error
            raise

    def accept_supplier_receipt(
        self,
        identity: SupplierIdentity,
        receipt: ValidatedSupplierReceipt,
        correlation_id: str,
    ) -> SupplierReceiptView:
        now = datetime.now(UTC)
        tenant_id = UUID(identity.tenant_id)
        with self._open_session() as session, session.begin():
            self._authorize_procurement_identity(session, identity)
            existing = session.execute(
                select(ProcurementSupplierReceipt).where(
                    ProcurementSupplierReceipt.tenant_id == tenant_id,
                    ProcurementSupplierReceipt.idempotency_key == receipt.idempotency_key,
                )
            ).scalar_one_or_none()
            if existing is not None:
                return self._receipt_view(session, existing)
            self._ensure_supplier(session, identity, receipt.supplier_id)
            warehouse = session.execute(
                select(PlatformWarehouse).where(
                    PlatformWarehouse.tenant_id == tenant_id,
                    PlatformWarehouse.id == UUID(receipt.warehouse_id),
                    PlatformWarehouse.status == "active",
                )
            ).scalar_one_or_none()
            if warehouse is None:
                raise ProcurementNotFound

            receipt_id = uuid4()
            accepted_lines: list[tuple[ProcurementSupplierReceiptLine, object]] = []
            line_records: list[ProcurementSupplierReceiptLine] = []
            seen_lot_codes: set[str] = set()
            for line in receipt.lines:
                self._ensure_ingredient_unit(
                    session, identity, line.ingredient_id, line.purchase_unit_id
                )
                status = line.status
                rejection_reason = line.rejection_reason
                duplicate = session.execute(
                    select(InventoryLot.id).where(
                        InventoryLot.tenant_id == tenant_id,
                        InventoryLot.warehouse_id == warehouse.id,
                        InventoryLot.lot_code == line.lot_code,
                    )
                ).scalar_one_or_none()
                if duplicate is not None or line.lot_code in seen_lot_codes:
                    status = "rejected"
                    rejection_reason = "duplicate_lot"
                seen_lot_codes.add(line.lot_code)
                accepted_quantity = (
                    line.accepted_quantity if status != "rejected" else Decimal("0")
                )
                line_record = ProcurementSupplierReceiptLine(
                    id=uuid4(),
                    tenant_id=tenant_id,
                    receipt_id=receipt_id,
                    ingredient_id=UUID(line.ingredient_id),
                    purchase_unit_id=UUID(line.purchase_unit_id),
                    lot_code=line.lot_code,
                    ordered_quantity=line.ordered_quantity,
                    delivered_quantity=line.delivered_quantity,
                    accepted_quantity=accepted_quantity,
                    remaining_quantity=line.ordered_quantity - accepted_quantity,
                    unit_cost=line.unit_cost,
                    expiry_date=line.expiry_date,
                    temperature=line.temperature,
                    status=status,
                    rejection_reason=rejection_reason,
                )
                line_records.append(line_record)
                if status != "rejected":
                    accepted_lines.append((line_record, line))

            statuses = {line.status for line in line_records}
            overall_status = (
                "rejected"
                if not accepted_lines
                else "accepted"
                if statuses == {"accepted"}
                else "partial"
            )
            receipt_record = ProcurementSupplierReceipt(
                id=receipt_id,
                tenant_id=tenant_id,
                idempotency_key=receipt.idempotency_key,
                order_reference=receipt.order_reference,
                supplier_id=UUID(receipt.supplier_id),
                warehouse_id=warehouse.id,
                received_on=receipt.received_on,
                status=overall_status,
                actor_id=UUID(identity.actor_id),
                correlation_id=correlation_id,
                accepted_at=now,
            )
            session.add(receipt_record)
            session.add_all(line_records)
            session.flush()
            transaction_id: UUID | None = None
            if accepted_lines:
                transaction_id = uuid4()
                session.add(
                    InventoryTransaction(
                        id=transaction_id,
                        tenant_id=tenant_id,
                        warehouse_id=warehouse.id,
                        source_receipt_id=receipt_id,
                        transaction_type="supplier_receipt",
                        actor_id=UUID(identity.actor_id),
                        correlation_id=correlation_id,
                        occurred_at=now,
                    )
                )
                session.flush()
                for line_record, line in accepted_lines:
                    lot_id = uuid4()
                    session.add(
                        InventoryLot(
                            id=lot_id,
                            tenant_id=tenant_id,
                            warehouse_id=warehouse.id,
                            ingredient_id=line_record.ingredient_id,
                            unit_id=line_record.purchase_unit_id,
                            lot_code=line_record.lot_code,
                            expiry_date=line_record.expiry_date,
                            unit_cost=line_record.unit_cost,
                            source_receipt_line_id=line_record.id,
                            created_at=now,
                        )
                    )
                    session.flush()
                    session.add(
                        InventoryEntry(
                            id=uuid4(),
                            tenant_id=tenant_id,
                            transaction_id=transaction_id,
                            lot_id=lot_id,
                            quantity=line.accepted_quantity,
                            unit_cost=line.unit_cost,
                        )
                    )
                    session.add(
                        InventoryStockBalance(
                            lot_id=lot_id,
                            tenant_id=tenant_id,
                            warehouse_id=warehouse.id,
                            quantity=line.accepted_quantity,
                            updated_at=now,
                        )
                    )
                session.add(
                    ControlOutboxEvent(
                        id=uuid4(),
                        tenant_id=tenant_id,
                        event_type="procurement.supplier_receipt.accepted",
                        aggregate_id=receipt_id,
                        payload={
                            "receiptId": str(receipt_id),
                            "inventoryTransactionId": str(transaction_id),
                        },
                        correlation_id=correlation_id,
                        status="pending",
                        attempts=0,
                        available_at=now,
                        created_at=now,
                        processed_at=None,
                        last_error=None,
                    )
                )
            session.flush()
            self._audit(
                session,
                identity,
                correlation_id,
                "procurement.supplier_receipt.accepted",
                str(receipt_id),
            )
            return self._receipt_view(session, receipt_record, transaction_id)

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
        if role not in {"tenant_admin", "branch_manager", "branch_operator"}:
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
    def _enqueue_cost_recalculation(
        session: Session,
        identity: SupplierIdentity,
        *,
        ingredient_id: UUID,
        offer_id: UUID,
        correlation_id: str,
    ) -> None:
        now = datetime.now(UTC)
        tenant_id = UUID(identity.tenant_id)
        payload = {"ingredientId": str(ingredient_id), "offerId": str(offer_id)}
        session.add(
            ControlOutboxEvent(
                id=uuid4(),
                tenant_id=tenant_id,
                event_type="procurement.supplier_offer.accepted",
                aggregate_id=offer_id,
                payload=payload,
                correlation_id=correlation_id,
                status="pending",
                attempts=0,
                available_at=now,
                created_at=now,
                processed_at=None,
                last_error=None,
            )
        )
        active_job = session.execute(
            select(ControlJob).where(
                ControlJob.tenant_id == tenant_id,
                ControlJob.job_type == "menu.cost_recalculation",
                ControlJob.dedup_key == str(ingredient_id),
                ControlJob.status.in_(("queued", "leased")),
            )
        ).scalar_one_or_none()
        if active_job is None:
            session.add(
                ControlJob(
                    id=uuid4(),
                    tenant_id=tenant_id,
                    job_type="menu.cost_recalculation",
                    dedup_key=str(ingredient_id),
                    payload=payload,
                    correlation_id=correlation_id,
                    status="queued",
                    attempts=0,
                    available_at=now,
                    lease_until=None,
                    leased_by=None,
                    last_error=None,
                    created_at=now,
                    updated_at=now,
                )
            )
        else:
            active_job.payload = payload
            active_job.correlation_id = correlation_id
            active_job.updated_at = now

        affected_versions = session.execute(
            select(MenuRecipeVersion.id)
            .join(
                MenuRecipeComponent,
                MenuRecipeComponent.recipe_version_id == MenuRecipeVersion.id,
            )
            .where(
                MenuRecipeVersion.tenant_id == tenant_id,
                MenuRecipeVersion.status == "approved",
                MenuRecipeComponent.ingredient_id == ingredient_id,
            )
        ).scalars()
        for recipe_version_id in set(affected_versions):
            statement = insert(MenuCostProjectionState).values(
                recipe_version_id=recipe_version_id,
                tenant_id=tenant_id,
                status="pending",
                updated_at=now,
                last_error=None,
            )
            session.execute(
                statement.on_conflict_do_update(
                    index_elements=[MenuCostProjectionState.recipe_version_id],
                    set_={"status": "stale", "updated_at": now, "last_error": None},
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

    @staticmethod
    def _receipt_view(
        session: Session,
        receipt: ProcurementSupplierReceipt,
        transaction_id: UUID | None = None,
    ) -> SupplierReceiptView:
        lines = tuple(
            session.execute(
                select(ProcurementSupplierReceiptLine)
                .where(ProcurementSupplierReceiptLine.receipt_id == receipt.id)
                .order_by(ProcurementSupplierReceiptLine.id)
            ).scalars()
        )
        if transaction_id is None:
            transaction_id = session.execute(
                select(InventoryTransaction.id).where(
                    InventoryTransaction.source_receipt_id == receipt.id
                )
            ).scalar_one_or_none()
        lot_by_line = {
            lot.source_receipt_line_id: lot
            for lot in session.execute(
                select(InventoryLot).where(
                    InventoryLot.source_receipt_line_id.in_([line.id for line in lines])
                )
            ).scalars()
        }
        return SupplierReceiptView(
            receipt_id=str(receipt.id),
            inventory_transaction_id=str(transaction_id) if transaction_id else None,
            idempotency_key=receipt.idempotency_key,
            order_reference=receipt.order_reference,
            status=receipt.status,
            lines=tuple(
                SupplierReceiptLineView(
                    receipt_line_id=str(line.id),
                    lot_id=str(lot_by_line[line.id].id) if line.id in lot_by_line else None,
                    lot_code=line.lot_code,
                    accepted_quantity=line.accepted_quantity,
                    remaining_quantity=line.remaining_quantity,
                    status=line.status,
                    rejection_reason=line.rejection_reason,
                )
                for line in lines
            ),
        )
