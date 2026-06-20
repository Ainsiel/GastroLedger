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
from gastroledger_api.modules.inventory_production.domain.production import (
    ProductionValidationError,
    StockLot,
    allocate_stock,
    validate_production_batch,
)
from gastroledger_api.technical.cost_projection_models import ControlOutboxEvent
from gastroledger_api.technical.inventory_models import (
    InventoryEntry,
    InventoryLot,
    InventoryProductionBatch,
    InventoryStockBalance,
    InventoryTransaction,
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
                    InventoryProductionBatch.idempotency_key
                    == command.idempotency_key.strip(),
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
                            StockLot(
                                str(lot.id), balance.quantity, lot.expiry_date, lot.created_at
                            )
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
