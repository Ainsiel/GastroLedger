from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import create_engine, select, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import NullPool

from gastroledger_api.modules.inventory_production.application.production import (
    PostProductionBatch,
    ProductionAuthorizationDenied,
    ProductionBatchView,
    ProductionConflict,
    ProductionIdentity,
    ProductionInsufficientStock,
    ProductionNotFound,
)
from gastroledger_api.modules.inventory_production.application.transfers import (
    TransferConflict,
    TransferIdentity,
    TransferInsufficientStock,
    TransferNotFound,
    TransferView,
)
from gastroledger_api.modules.inventory_production.domain.production import (
    ProductionValidationError,
    StockLot,
    allocate_stock,
    validate_production_batch,
)
from gastroledger_api.modules.inventory_production.domain.transfers import (
    TransferState,
    TransferValidationError,
    ValidatedTransferRequest,
    approve_transfer,
    dispatch_transfer,
    receive_transfer,
)
from gastroledger_api.technical.cost_projection_models import ControlOutboxEvent
from gastroledger_api.technical.inventory_models import (
    InventoryEntry,
    InventoryLot,
    InventoryProductionBatch,
    InventoryStockBalance,
    InventoryTransaction,
    InventoryTransfer,
    InventoryTransferLine,
)
from gastroledger_api.technical.menu_models import (
    MenuRecipe,
    MenuRecipeComponent,
    MenuRecipeVersion,
)
from gastroledger_api.technical.platform_models import (
    ControlAuditEvent,
    PlatformMembership,
    PlatformWarehouse,
)
from gastroledger_api.technical.postgres_platform import sqlalchemy_database_url


class PostgresInventoryStore:
    def __init__(self, database_url: str) -> None:
        self._database_url = database_url
        self._engine: Engine | None = None

    def _open_session(self) -> Session:
        if self._engine is None:
            self._engine = create_engine(
                sqlalchemy_database_url(self._database_url), poolclass=NullPool
            )
        return Session(self._engine)

    def post_batch(
        self,
        identity: ProductionIdentity,
        command: PostProductionBatch,
        correlation_id: str,
    ) -> ProductionBatchView:
        tenant_id = UUID(identity.tenant_id)
        now = datetime.now(UTC)
        with self._open_session() as session, session.begin():
            self._authorize(session, identity)
            existing = session.execute(
                select(InventoryProductionBatch).where(
                    InventoryProductionBatch.tenant_id == tenant_id,
                    InventoryProductionBatch.idempotency_key == command.idempotency_key.strip(),
                )
            ).scalar_one_or_none()
            if existing is not None:
                return self._batch_view(session, existing)

            warehouse = session.execute(
                select(PlatformWarehouse).where(
                    PlatformWarehouse.tenant_id == tenant_id,
                    PlatformWarehouse.id == UUID(command.warehouse_id),
                    PlatformWarehouse.status == "active",
                )
            ).scalar_one_or_none()
            recipe_row = session.execute(
                select(MenuRecipeVersion, MenuRecipe)
                .join(MenuRecipe, MenuRecipe.id == MenuRecipeVersion.recipe_id)
                .where(
                    MenuRecipeVersion.tenant_id == tenant_id,
                    MenuRecipeVersion.id == UUID(command.recipe_version_id),
                    MenuRecipeVersion.status == "approved",
                    MenuRecipeVersion.effective_from <= command.produced_on,
                    MenuRecipe.recipe_type == "sub_recipe",
                )
            ).one_or_none()
            if warehouse is None or recipe_row is None:
                raise ProductionNotFound
            recipe_version, _recipe = recipe_row
            validated = validate_production_batch(
                idempotency_key=command.idempotency_key,
                batch_number=command.batch_number,
                warehouse_id=command.warehouse_id,
                recipe_version_id=command.recipe_version_id,
                actual_yield=command.actual_yield,
                output_lot_code=command.output_lot_code,
                produced_on=command.produced_on,
                variance_reason=command.variance_reason,
                expected_yield=recipe_version.yield_quantity,
            )
            duplicate = session.execute(
                select(InventoryProductionBatch.id).where(
                    InventoryProductionBatch.tenant_id == tenant_id,
                    InventoryProductionBatch.batch_number == validated.batch_number,
                )
            ).scalar_one_or_none()
            duplicate_lot = session.execute(
                select(InventoryLot.id).where(
                    InventoryLot.tenant_id == tenant_id,
                    InventoryLot.warehouse_id == warehouse.id,
                    InventoryLot.lot_code == validated.output_lot_code,
                )
            ).scalar_one_or_none()
            if duplicate is not None or duplicate_lot is not None:
                raise ProductionConflict

            components = tuple(
                session.execute(
                    select(MenuRecipeComponent).where(
                        MenuRecipeComponent.tenant_id == tenant_id,
                        MenuRecipeComponent.recipe_version_id == recipe_version.id,
                    )
                ).scalars()
            )
            if not components or any(
                component.component_type != "ingredient" for component in components
            ):
                raise ProductionNotFound

            planned: list[tuple[InventoryLot, InventoryStockBalance, Decimal]] = []
            try:
                for component in components:
                    rows = tuple(
                        session.execute(
                            select(InventoryLot, InventoryStockBalance)
                            .join(
                                InventoryStockBalance,
                                InventoryStockBalance.lot_id == InventoryLot.id,
                            )
                            .where(
                                InventoryLot.tenant_id == tenant_id,
                                InventoryLot.warehouse_id == warehouse.id,
                                InventoryLot.ingredient_id == component.ingredient_id,
                                InventoryLot.unit_id == component.unit_id,
                                InventoryStockBalance.quantity > 0,
                            )
                            .with_for_update(of=InventoryStockBalance)
                        ).all()
                    )
                    allocations = allocate_stock(
                        tuple(
                            StockLot(str(lot.id), balance.quantity, lot.expiry_date, lot.created_at)
                            for lot, balance in rows
                        ),
                        component.quantity,
                    )
                    row_by_id = {str(lot.id): (lot, balance) for lot, balance in rows}
                    for allocation in allocations:
                        lot, balance = row_by_id[allocation.lot_id]
                        planned.append((lot, balance, allocation.quantity))
            except ProductionValidationError as error:
                if any(detail.code == "insufficient_stock" for detail in error.details):
                    raise ProductionInsufficientStock from error
                raise

            batch_id = uuid4()
            transaction_id = uuid4()
            output_lot_id = uuid4()
            batch = InventoryProductionBatch(
                id=batch_id,
                tenant_id=tenant_id,
                idempotency_key=validated.idempotency_key,
                batch_number=validated.batch_number,
                warehouse_id=warehouse.id,
                recipe_version_id=recipe_version.id,
                expected_yield=validated.expected_yield,
                actual_yield=validated.actual_yield,
                variance_quantity=validated.variance_quantity,
                variance_reason=validated.variance_reason,
                output_lot_code=validated.output_lot_code,
                produced_on=validated.produced_on,
                status="posted",
                actor_id=UUID(identity.actor_id),
                correlation_id=correlation_id,
                posted_at=now,
            )
            session.add(batch)
            session.flush()
            session.add(
                InventoryTransaction(
                    id=transaction_id,
                    tenant_id=tenant_id,
                    warehouse_id=warehouse.id,
                    source_receipt_id=None,
                    source_production_batch_id=batch_id,
                    transaction_type="production",
                    actor_id=UUID(identity.actor_id),
                    correlation_id=correlation_id,
                    occurred_at=now,
                )
            )
            session.flush()
            total_cost = Decimal("0")
            for lot, balance, quantity in planned:
                balance.quantity -= quantity
                balance.updated_at = now
                total_cost += quantity * lot.unit_cost
                session.add(
                    InventoryEntry(
                        id=uuid4(),
                        tenant_id=tenant_id,
                        transaction_id=transaction_id,
                        lot_id=lot.id,
                        quantity=-quantity,
                        unit_cost=lot.unit_cost,
                    )
                )
            output_unit_cost = total_cost / validated.actual_yield
            session.add(
                InventoryLot(
                    id=output_lot_id,
                    tenant_id=tenant_id,
                    warehouse_id=warehouse.id,
                    ingredient_id=None,
                    prepared_recipe_version_id=recipe_version.id,
                    unit_id=recipe_version.yield_unit_id,
                    lot_code=validated.output_lot_code,
                    expiry_date=None,
                    unit_cost=output_unit_cost,
                    source_receipt_line_id=None,
                    source_production_batch_id=batch_id,
                    created_at=now,
                )
            )
            session.flush()
            session.add_all(
                [
                    InventoryEntry(
                        id=uuid4(),
                        tenant_id=tenant_id,
                        transaction_id=transaction_id,
                        lot_id=output_lot_id,
                        quantity=validated.actual_yield,
                        unit_cost=output_unit_cost,
                    ),
                    InventoryStockBalance(
                        lot_id=output_lot_id,
                        tenant_id=tenant_id,
                        warehouse_id=warehouse.id,
                        quantity=validated.actual_yield,
                        updated_at=now,
                    ),
                    ControlOutboxEvent(
                        id=uuid4(),
                        tenant_id=tenant_id,
                        event_type="inventory.production_batch.posted",
                        aggregate_id=batch_id,
                        payload={
                            "productionBatchId": str(batch_id),
                            "inventoryTransactionId": str(transaction_id),
                            "outputLotId": str(output_lot_id),
                        },
                        correlation_id=correlation_id,
                        status="pending",
                        attempts=0,
                        available_at=now,
                        created_at=now,
                        processed_at=None,
                        last_error=None,
                    ),
                    ControlAuditEvent(
                        id=uuid4(),
                        tenant_id=tenant_id,
                        actor_id=UUID(identity.actor_id),
                        correlation_id=correlation_id,
                        action="inventory.production_batch.posted",
                        object_reference=str(batch_id),
                        occurred_at=now,
                    ),
                ]
            )
            session.flush()
            return self._batch_view(session, batch, transaction_id, output_lot_id)

    def request_transfer(
        self, identity: TransferIdentity, transfer: ValidatedTransferRequest, correlation_id: str
    ) -> TransferView:
        tenant_id, now = UUID(identity.tenant_id), datetime.now(UTC)
        with self._open_session() as session, session.begin():
            self._authorize(session, identity)
            warehouses = set(
                session.execute(
                    select(PlatformWarehouse.id).where(
                        PlatformWarehouse.tenant_id == tenant_id,
                        PlatformWarehouse.id.in_(
                            (
                                UUID(transfer.source_warehouse_id),
                                UUID(transfer.destination_warehouse_id),
                            )
                        ),
                        PlatformWarehouse.status == "active",
                    )
                ).scalars()
            )
            if len(warehouses) != 2:
                raise TransferNotFound
            if session.execute(
                select(InventoryTransfer.id).where(
                    InventoryTransfer.tenant_id == tenant_id,
                    InventoryTransfer.transfer_number == transfer.transfer_number,
                )
            ).scalar_one_or_none():
                raise TransferConflict
            transfer_id = uuid4()
            record = InventoryTransfer(
                id=transfer_id,
                tenant_id=tenant_id,
                transfer_number=transfer.transfer_number,
                source_warehouse_id=UUID(transfer.source_warehouse_id),
                destination_warehouse_id=UUID(transfer.destination_warehouse_id),
                status="requested",
                requested_by=UUID(identity.actor_id),
                approved_by=None,
                correlation_id=correlation_id,
                created_at=now,
                updated_at=now,
            )
            line = InventoryTransferLine(
                id=uuid4(),
                tenant_id=tenant_id,
                transfer_id=transfer_id,
                item_type=transfer.item_type,
                item_id=UUID(transfer.item_id),
                unit_id=UUID(transfer.unit_id),
                requested_quantity=transfer.requested_quantity,
                approved_quantity=Decimal("0"),
                dispatched_quantity=Decimal("0"),
                received_quantity=Decimal("0"),
                loss_quantity=Decimal("0"),
                loss_reason=None,
            )
            session.add_all((record, line))
            session.flush()
            self._transfer_audit(
                session, identity, correlation_id, "inventory.transfer.requested", transfer_id
            )
            return self._transfer_view(record, line)

    def approve_transfer(
        self, identity: TransferIdentity, transfer_id: str, quantity: Decimal, correlation_id: str
    ) -> TransferView:
        with self._open_session() as session, session.begin():
            self._authorize(session, identity)
            record, line = self._locked_transfer(session, identity, transfer_id)
            state = approve_transfer(self._state(record, line), quantity)
            record.status, record.approved_by, record.updated_at = (
                state.status,
                UUID(identity.actor_id),
                datetime.now(UTC),
            )
            line.approved_quantity = state.approved_quantity
            self._transfer_audit(
                session, identity, correlation_id, "inventory.transfer.approved", record.id
            )
            return self._transfer_view(record, line)

    def dispatch_transfer(
        self,
        identity: TransferIdentity,
        transfer_id: str,
        command_key: str,
        quantity: Decimal,
        correlation_id: str,
    ) -> TransferView:
        tenant_id, now = UUID(identity.tenant_id), datetime.now(UTC)
        with self._open_session() as session, session.begin():
            self._authorize(session, identity)
            existing = session.execute(
                select(InventoryTransaction.id).where(
                    InventoryTransaction.tenant_id == tenant_id,
                    InventoryTransaction.command_key == command_key,
                )
            ).scalar_one_or_none()
            record, line = self._locked_transfer(session, identity, transfer_id)
            if existing:
                return self._transfer_view(record, line)
            try:
                state = dispatch_transfer(self._state(record, line), quantity)
            except TransferValidationError as error:
                raise TransferConflict from error
            item_filter = (
                InventoryLot.ingredient_id == line.item_id
                if line.item_type == "ingredient"
                else InventoryLot.prepared_recipe_version_id == line.item_id
            )
            rows = tuple(
                session.execute(
                    select(InventoryLot, InventoryStockBalance)
                    .join(InventoryStockBalance, InventoryStockBalance.lot_id == InventoryLot.id)
                    .where(
                        InventoryLot.tenant_id == tenant_id,
                        InventoryLot.warehouse_id == record.source_warehouse_id,
                        InventoryLot.unit_id == line.unit_id,
                        item_filter,
                        InventoryStockBalance.quantity > 0,
                    )
                    .with_for_update(of=InventoryStockBalance)
                ).all()
            )
            try:
                allocations = allocate_stock(
                    tuple(
                        StockLot(
                            str(lot.id), balance.quantity, lot.expiry_date, lot.created_at
                        )
                        for lot, balance in rows
                    ),
                    quantity,
                )
            except ProductionValidationError as error:
                raise TransferInsufficientStock from error
            tx_id = uuid4()
            session.add(
                InventoryTransaction(
                    id=tx_id,
                    tenant_id=tenant_id,
                    warehouse_id=record.source_warehouse_id,
                    source_receipt_id=None,
                    source_production_batch_id=None,
                    source_transfer_id=record.id,
                    command_key=command_key,
                    transaction_type="transfer_dispatch",
                    actor_id=UUID(identity.actor_id),
                    correlation_id=correlation_id,
                    occurred_at=now,
                )
            )
            session.flush()
            by_id = {str(lot.id): (lot, balance) for lot, balance in rows}
            for allocation in allocations:
                lot, balance = by_id[allocation.lot_id]
                balance.quantity -= allocation.quantity
                balance.updated_at = now
                session.add(
                    InventoryEntry(
                        id=uuid4(),
                        tenant_id=tenant_id,
                        transaction_id=tx_id,
                        lot_id=lot.id,
                        quantity=-allocation.quantity,
                        unit_cost=lot.unit_cost,
                    )
                )
            line.dispatched_quantity, record.status, record.updated_at = (
                state.dispatched_quantity,
                state.status,
                now,
            )
            self._transfer_audit(
                session, identity, correlation_id, "inventory.transfer.dispatched", record.id
            )
            return self._transfer_view(record, line)

    def receive_transfer(
        self,
        identity: TransferIdentity,
        transfer_id: str,
        command_key: str,
        received: Decimal,
        loss: Decimal,
        reason: str,
        correlation_id: str,
    ) -> TransferView:
        tenant_id, now = UUID(identity.tenant_id), datetime.now(UTC)
        with self._open_session() as session, session.begin():
            self._authorize(session, identity)
            existing = session.execute(
                select(InventoryTransaction.id).where(
                    InventoryTransaction.tenant_id == tenant_id,
                    InventoryTransaction.command_key == command_key,
                )
            ).scalar_one_or_none()
            record, line = self._locked_transfer(session, identity, transfer_id)
            if existing:
                return self._transfer_view(record, line)
            try:
                state = receive_transfer(self._state(record, line), received, loss, reason)
            except TransferValidationError as error:
                raise TransferConflict from error
            tx_id = uuid4()
            session.add(
                InventoryTransaction(
                    id=tx_id,
                    tenant_id=tenant_id,
                    warehouse_id=record.destination_warehouse_id,
                    source_receipt_id=None,
                    source_production_batch_id=None,
                    source_transfer_id=record.id,
                    command_key=command_key,
                    transaction_type="transfer_receipt",
                    actor_id=UUID(identity.actor_id),
                    correlation_id=correlation_id,
                    occurred_at=now,
                )
            )
            session.flush()
            remaining = received
            dispatch_entries = tuple(
                session.execute(
                    select(InventoryEntry, InventoryLot)
                    .join(
                        InventoryTransaction,
                        InventoryTransaction.id == InventoryEntry.transaction_id,
                    )
                    .join(InventoryLot, InventoryLot.id == InventoryEntry.lot_id)
                    .where(
                        InventoryTransaction.source_transfer_id == record.id,
                        InventoryTransaction.transaction_type == "transfer_dispatch",
                    )
                    .order_by(InventoryTransaction.occurred_at, InventoryEntry.id)
                ).all()
            )
            for entry, source_lot in dispatch_entries:
                if remaining <= 0:
                    break
                destination_lot = session.execute(
                    select(InventoryLot).where(
                        InventoryLot.tenant_id == tenant_id,
                        InventoryLot.warehouse_id == record.destination_warehouse_id,
                        InventoryLot.source_transfer_id == record.id,
                        InventoryLot.source_lot_id == source_lot.id,
                    )
                ).scalar_one_or_none()
                already = (
                    Decimal("0")
                    if destination_lot is None
                    else session.execute(
                        select(InventoryEntry.quantity).where(
                            InventoryEntry.lot_id == destination_lot.id, InventoryEntry.quantity > 0
                        )
                    )
                    .scalars()
                    .all()
                )
                already_total = (
                    sum(already, Decimal("0")) if not isinstance(already, Decimal) else already
                )
                available = -entry.quantity - already_total
                quantity = min(available, remaining)
                if quantity <= 0:
                    continue
                if destination_lot is None:
                    destination_lot = InventoryLot(
                        id=uuid4(),
                        tenant_id=tenant_id,
                        warehouse_id=record.destination_warehouse_id,
                        ingredient_id=source_lot.ingredient_id,
                        prepared_recipe_version_id=source_lot.prepared_recipe_version_id,
                        unit_id=source_lot.unit_id,
                        lot_code=f"{record.transfer_number}-{source_lot.lot_code}",
                        expiry_date=source_lot.expiry_date,
                        unit_cost=source_lot.unit_cost,
                        source_receipt_line_id=None,
                        source_production_batch_id=None,
                        source_transfer_id=record.id,
                        source_lot_id=source_lot.id,
                        created_at=now,
                    )
                    session.add(destination_lot)
                    session.flush()
                    balance = InventoryStockBalance(
                        lot_id=destination_lot.id,
                        tenant_id=tenant_id,
                        warehouse_id=record.destination_warehouse_id,
                        quantity=Decimal("0"),
                        updated_at=now,
                    )
                    session.add(balance)
                else:
                    balance = session.execute(
                        select(InventoryStockBalance)
                        .where(InventoryStockBalance.lot_id == destination_lot.id)
                        .with_for_update()
                    ).scalar_one()
                balance.quantity += quantity
                balance.updated_at = now
                session.add(
                    InventoryEntry(
                        id=uuid4(),
                        tenant_id=tenant_id,
                        transaction_id=tx_id,
                        lot_id=destination_lot.id,
                        quantity=quantity,
                        unit_cost=source_lot.unit_cost,
                    )
                )
                remaining -= quantity
            if remaining > 0:
                raise TransferConflict
            line.received_quantity, line.loss_quantity, line.loss_reason = (
                state.received_quantity,
                state.loss_quantity,
                reason.strip() or line.loss_reason,
            )
            record.status, record.updated_at = state.status, now
            self._transfer_audit(
                session, identity, correlation_id, "inventory.transfer.received", record.id
            )
            return self._transfer_view(record, line)

    def _locked_transfer(self, session: Session, identity: TransferIdentity, transfer_id: str):
        record = session.execute(
            select(InventoryTransfer)
            .where(
                InventoryTransfer.tenant_id == UUID(identity.tenant_id),
                InventoryTransfer.id == UUID(transfer_id),
            )
            .with_for_update()
        ).scalar_one_or_none()
        if record is None:
            raise TransferNotFound
        line = session.execute(
            select(InventoryTransferLine)
            .where(InventoryTransferLine.transfer_id == record.id)
            .with_for_update()
        ).scalar_one()
        return record, line

    @staticmethod
    def _state(record, line):
        return TransferState(
            record.status,
            line.requested_quantity,
            line.approved_quantity,
            line.dispatched_quantity,
            line.received_quantity,
            line.loss_quantity,
        )

    @staticmethod
    def _transfer_view(record, line):
        return TransferView(
            str(record.id),
            record.transfer_number,
            record.status,
            str(record.source_warehouse_id),
            str(record.destination_warehouse_id),
            line.item_type,
            str(line.item_id),
            str(line.unit_id),
            line.requested_quantity,
            line.approved_quantity,
            line.dispatched_quantity,
            line.received_quantity,
            line.loss_quantity,
        )

    @staticmethod
    def _transfer_audit(session, identity, correlation_id, action, transfer_id):
        session.add(
            ControlAuditEvent(
                id=uuid4(),
                tenant_id=UUID(identity.tenant_id),
                actor_id=UUID(identity.actor_id),
                correlation_id=correlation_id,
                action=action,
                object_reference=str(transfer_id),
                occurred_at=datetime.now(UTC),
            )
        )

    @staticmethod
    def _authorize(session: Session, identity: ProductionIdentity) -> None:
        session.execute(text("set local role gastroledger_app"))
        session.execute(
            text("select set_config('app.current_tenant_id', :tenant_id, true)"),
            {"tenant_id": identity.tenant_id},
        )
        role = session.execute(
            select(PlatformMembership.role).where(
                PlatformMembership.tenant_id == UUID(identity.tenant_id),
                PlatformMembership.user_id == UUID(identity.actor_id),
            )
        ).scalar_one_or_none()
        if role not in {"tenant_admin", "branch_manager", "branch_operator"}:
            raise ProductionAuthorizationDenied

    @staticmethod
    def _batch_view(
        session: Session,
        batch: InventoryProductionBatch,
        transaction_id: UUID | None = None,
        output_lot_id: UUID | None = None,
    ) -> ProductionBatchView:
        if transaction_id is None:
            transaction_id = session.execute(
                select(InventoryTransaction.id).where(
                    InventoryTransaction.source_production_batch_id == batch.id
                )
            ).scalar_one()
        if output_lot_id is None:
            output_lot_id = session.execute(
                select(InventoryLot.id).where(
                    InventoryLot.source_production_batch_id == batch.id,
                    InventoryLot.prepared_recipe_version_id.is_not(None),
                )
            ).scalar_one()
        consumed = sum(
            (
                -quantity
                for quantity in session.execute(
                    select(InventoryEntry.quantity).where(
                        InventoryEntry.transaction_id == transaction_id,
                        InventoryEntry.quantity < 0,
                    )
                ).scalars()
            ),
            Decimal("0"),
        )
        return ProductionBatchView(
            production_batch_id=str(batch.id),
            inventory_transaction_id=str(transaction_id),
            output_lot_id=str(output_lot_id),
            batch_number=batch.batch_number,
            status=batch.status,
            recipe_version_id=str(batch.recipe_version_id),
            expected_yield=batch.expected_yield,
            actual_yield=batch.actual_yield,
            variance_quantity=batch.variance_quantity,
            variance_reason=batch.variance_reason,
            consumed_quantity=consumed,
        )
