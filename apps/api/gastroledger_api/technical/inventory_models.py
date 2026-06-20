from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Numeric,
    Text,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column

from gastroledger_api.technical.platform_models import Base


class InventoryTransaction(Base):
    __tablename__ = "inventory_transactions"
    __table_args__ = (
        ForeignKeyConstraint(
            ["warehouse_id", "tenant_id"],
            ["platform_warehouses.id", "platform_warehouses.tenant_id"],
        ),
        ForeignKeyConstraint(
            ["source_receipt_id", "tenant_id"],
            ["procurement_supplier_receipts.id", "procurement_supplier_receipts.tenant_id"],
        ),
        ForeignKeyConstraint(
            ["source_production_batch_id", "tenant_id"],
            ["inventory_production_batches.id", "inventory_production_batches.tenant_id"],
        ),
        ForeignKeyConstraint(
            ["source_transfer_id", "tenant_id"],
            ["inventory_transfers.id", "inventory_transfers.tenant_id"],
        ),
        ForeignKeyConstraint(
            ["source_waste_id", "tenant_id"],
            ["inventory_waste_records.id", "inventory_waste_records.tenant_id"],
        ),
        CheckConstraint(
            "(transaction_type = 'supplier_receipt' AND source_receipt_id IS NOT NULL "
            "AND source_production_batch_id IS NULL) OR "
            "(transaction_type = 'production' AND source_receipt_id IS NULL "
            "AND source_production_batch_id IS NOT NULL AND source_transfer_id IS NULL) OR "
            "(transaction_type IN ('transfer_dispatch', 'transfer_receipt') "
            "AND source_receipt_id IS NULL AND source_production_batch_id IS NULL "
            "AND source_transfer_id IS NOT NULL AND source_waste_id IS NULL) OR "
            "(transaction_type IN ('waste', 'waste_correction') "
            "AND source_receipt_id IS NULL AND source_production_batch_id IS NULL "
            "AND source_transfer_id IS NULL AND source_waste_id IS NOT NULL)"
        ),
        UniqueConstraint("tenant_id", "source_receipt_id"),
        UniqueConstraint("tenant_id", "source_production_batch_id"),
        UniqueConstraint("tenant_id", "command_key"),
        UniqueConstraint("id", "tenant_id"),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("platform_tenants.id"))
    warehouse_id: Mapped[UUID] = mapped_column(Uuid)
    source_receipt_id: Mapped[UUID | None] = mapped_column(Uuid)
    source_production_batch_id: Mapped[UUID | None] = mapped_column(Uuid)
    source_transfer_id: Mapped[UUID | None] = mapped_column(Uuid)
    command_key: Mapped[str | None] = mapped_column(Text)
    source_waste_id: Mapped[UUID | None] = mapped_column(Uuid)
    transaction_type: Mapped[str] = mapped_column(Text)
    actor_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("platform_users.id"))
    correlation_id: Mapped[str] = mapped_column(Text)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class InventoryLot(Base):
    __tablename__ = "inventory_lots"
    __table_args__ = (
        ForeignKeyConstraint(
            ["warehouse_id", "tenant_id"],
            ["platform_warehouses.id", "platform_warehouses.tenant_id"],
        ),
        ForeignKeyConstraint(
            ["ingredient_id", "tenant_id"],
            ["menu_ingredients.id", "menu_ingredients.tenant_id"],
        ),
        ForeignKeyConstraint(
            ["unit_id", "tenant_id"],
            ["menu_units.id", "menu_units.tenant_id"],
        ),
        ForeignKeyConstraint(
            ["source_receipt_line_id", "tenant_id"],
            [
                "procurement_supplier_receipt_lines.id",
                "procurement_supplier_receipt_lines.tenant_id",
            ],
        ),
        ForeignKeyConstraint(
            ["prepared_recipe_version_id", "tenant_id"],
            ["menu_recipe_versions.id", "menu_recipe_versions.tenant_id"],
        ),
        ForeignKeyConstraint(
            ["source_production_batch_id", "tenant_id"],
            ["inventory_production_batches.id", "inventory_production_batches.tenant_id"],
        ),
        ForeignKeyConstraint(
            ["source_transfer_id", "tenant_id"],
            ["inventory_transfers.id", "inventory_transfers.tenant_id"],
        ),
        ForeignKeyConstraint(
            ["source_lot_id", "tenant_id"], ["inventory_lots.id", "inventory_lots.tenant_id"]
        ),
        CheckConstraint(
            "(ingredient_id IS NOT NULL AND prepared_recipe_version_id IS NULL) OR "
            "(ingredient_id IS NULL AND prepared_recipe_version_id IS NOT NULL)"
        ),
        CheckConstraint(
            "(source_receipt_line_id IS NOT NULL AND source_production_batch_id IS NULL) OR "
            "(source_receipt_line_id IS NULL AND source_production_batch_id IS NOT NULL "
            "AND source_transfer_id IS NULL) OR "
            "(source_receipt_line_id IS NULL AND source_production_batch_id IS NULL "
            "AND source_transfer_id IS NOT NULL)"
        ),
        CheckConstraint("unit_cost > 0"),
        UniqueConstraint("tenant_id", "warehouse_id", "lot_code"),
        UniqueConstraint("id", "tenant_id"),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("platform_tenants.id"))
    warehouse_id: Mapped[UUID] = mapped_column(Uuid)
    ingredient_id: Mapped[UUID | None] = mapped_column(Uuid)
    prepared_recipe_version_id: Mapped[UUID | None] = mapped_column(Uuid)
    unit_id: Mapped[UUID] = mapped_column(Uuid)
    lot_code: Mapped[str] = mapped_column(Text)
    expiry_date: Mapped[date | None] = mapped_column(Date)
    unit_cost: Mapped[Decimal] = mapped_column(Numeric(24, 10))
    source_receipt_line_id: Mapped[UUID | None] = mapped_column(Uuid)
    source_production_batch_id: Mapped[UUID | None] = mapped_column(Uuid)
    source_transfer_id: Mapped[UUID | None] = mapped_column(Uuid)
    source_lot_id: Mapped[UUID | None] = mapped_column(Uuid)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class InventoryEntry(Base):
    __tablename__ = "inventory_entries"
    __table_args__ = (
        ForeignKeyConstraint(
            ["transaction_id", "tenant_id"],
            ["inventory_transactions.id", "inventory_transactions.tenant_id"],
        ),
        ForeignKeyConstraint(
            ["lot_id", "tenant_id"],
            ["inventory_lots.id", "inventory_lots.tenant_id"],
        ),
        CheckConstraint("quantity <> 0"),
        CheckConstraint("unit_cost > 0"),
        UniqueConstraint("tenant_id", "transaction_id", "lot_id"),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("platform_tenants.id"))
    transaction_id: Mapped[UUID] = mapped_column(Uuid)
    lot_id: Mapped[UUID] = mapped_column(Uuid)
    quantity: Mapped[Decimal] = mapped_column(Numeric(24, 10))
    unit_cost: Mapped[Decimal] = mapped_column(Numeric(24, 10))


class InventoryStockBalance(Base):
    __tablename__ = "inventory_stock_balances"
    __table_args__ = (
        ForeignKeyConstraint(
            ["lot_id", "tenant_id"],
            ["inventory_lots.id", "inventory_lots.tenant_id"],
        ),
        ForeignKeyConstraint(
            ["warehouse_id", "tenant_id"],
            ["platform_warehouses.id", "platform_warehouses.tenant_id"],
        ),
        CheckConstraint("quantity >= 0"),
    )

    lot_id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("platform_tenants.id"))
    warehouse_id: Mapped[UUID] = mapped_column(Uuid)
    quantity: Mapped[Decimal] = mapped_column(Numeric(24, 10))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class InventoryProductionBatch(Base):
    __tablename__ = "inventory_production_batches"
    __table_args__ = (
        ForeignKeyConstraint(
            ["warehouse_id", "tenant_id"],
            ["platform_warehouses.id", "platform_warehouses.tenant_id"],
        ),
        ForeignKeyConstraint(
            ["recipe_version_id", "tenant_id"],
            ["menu_recipe_versions.id", "menu_recipe_versions.tenant_id"],
        ),
        CheckConstraint("expected_yield > 0"),
        CheckConstraint("actual_yield > 0"),
        CheckConstraint("status = 'posted'"),
        UniqueConstraint("tenant_id", "idempotency_key"),
        UniqueConstraint("tenant_id", "batch_number"),
        UniqueConstraint("id", "tenant_id"),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("platform_tenants.id"))
    idempotency_key: Mapped[str] = mapped_column(Text)
    batch_number: Mapped[str] = mapped_column(Text)
    warehouse_id: Mapped[UUID] = mapped_column(Uuid)
    recipe_version_id: Mapped[UUID] = mapped_column(Uuid)
    expected_yield: Mapped[Decimal] = mapped_column(Numeric(24, 10))
    actual_yield: Mapped[Decimal] = mapped_column(Numeric(24, 10))
    variance_quantity: Mapped[Decimal] = mapped_column(Numeric(24, 10))
    variance_reason: Mapped[str | None] = mapped_column(Text)
    output_lot_code: Mapped[str] = mapped_column(Text)
    produced_on: Mapped[date] = mapped_column(Date)
    status: Mapped[str] = mapped_column(Text)
    actor_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("platform_users.id"))
    correlation_id: Mapped[str] = mapped_column(Text)
    posted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class InventoryTransfer(Base):
    __tablename__ = "inventory_transfers"
    __table_args__ = (
        ForeignKeyConstraint(
            ["source_warehouse_id", "tenant_id"],
            ["platform_warehouses.id", "platform_warehouses.tenant_id"],
        ),
        ForeignKeyConstraint(
            ["destination_warehouse_id", "tenant_id"],
            ["platform_warehouses.id", "platform_warehouses.tenant_id"],
        ),
        CheckConstraint("source_warehouse_id <> destination_warehouse_id"),
        UniqueConstraint("tenant_id", "transfer_number"),
        UniqueConstraint("id", "tenant_id"),
    )
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("platform_tenants.id"))
    transfer_number: Mapped[str] = mapped_column(Text)
    source_warehouse_id: Mapped[UUID] = mapped_column(Uuid)
    destination_warehouse_id: Mapped[UUID] = mapped_column(Uuid)
    status: Mapped[str] = mapped_column(Text)
    requested_by: Mapped[UUID] = mapped_column(Uuid, ForeignKey("platform_users.id"))
    approved_by: Mapped[UUID | None] = mapped_column(Uuid, ForeignKey("platform_users.id"))
    correlation_id: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class InventoryTransferLine(Base):
    __tablename__ = "inventory_transfer_lines"
    __table_args__ = (
        ForeignKeyConstraint(
            ["transfer_id", "tenant_id"],
            ["inventory_transfers.id", "inventory_transfers.tenant_id"],
        ),
        CheckConstraint("item_type IN ('ingredient', 'prepared_recipe')"),
        CheckConstraint(
            "requested_quantity > 0 AND approved_quantity >= 0 "
            "AND dispatched_quantity >= 0 AND received_quantity >= 0 "
            "AND loss_quantity >= 0"
        ),
        CheckConstraint(
            "approved_quantity <= requested_quantity "
            "AND dispatched_quantity <= approved_quantity "
            "AND received_quantity + loss_quantity <= dispatched_quantity"
        ),
        UniqueConstraint("transfer_id"),
    )
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("platform_tenants.id"))
    transfer_id: Mapped[UUID] = mapped_column(Uuid)
    item_type: Mapped[str] = mapped_column(Text)
    item_id: Mapped[UUID] = mapped_column(Uuid)
    unit_id: Mapped[UUID] = mapped_column(Uuid)
    requested_quantity: Mapped[Decimal] = mapped_column(Numeric(24, 10))
    approved_quantity: Mapped[Decimal] = mapped_column(Numeric(24, 10))
    dispatched_quantity: Mapped[Decimal] = mapped_column(Numeric(24, 10))
    received_quantity: Mapped[Decimal] = mapped_column(Numeric(24, 10))
    loss_quantity: Mapped[Decimal] = mapped_column(Numeric(24, 10))
    loss_reason: Mapped[str | None] = mapped_column(Text)


class InventoryWasteRecord(Base):
    __tablename__ = "inventory_waste_records"
    __table_args__ = (
        ForeignKeyConstraint(
            ["warehouse_id", "tenant_id"],
            ["platform_warehouses.id", "platform_warehouses.tenant_id"],
        ),
        ForeignKeyConstraint(
            ["lot_id", "tenant_id"],
            ["inventory_lots.id", "inventory_lots.tenant_id"],
        ),
        CheckConstraint("quantity > 0 AND unit_cost > 0"),
        CheckConstraint("status IN ('pending_approval','posted','rejected','corrected')"),
        UniqueConstraint("tenant_id", "command_key"),
        UniqueConstraint("id", "tenant_id"),
    )
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("platform_tenants.id"))
    command_key: Mapped[str] = mapped_column(Text)
    warehouse_id: Mapped[UUID] = mapped_column(Uuid)
    lot_id: Mapped[UUID] = mapped_column(Uuid)
    quantity: Mapped[Decimal] = mapped_column(Numeric(24, 10))
    unit_cost: Mapped[Decimal] = mapped_column(Numeric(24, 10))
    reason: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(Text)
    requested_by: Mapped[UUID] = mapped_column(Uuid, ForeignKey("platform_users.id"))
    decision_by: Mapped[UUID | None] = mapped_column(Uuid, ForeignKey("platform_users.id"))
    decision_reason: Mapped[str | None] = mapped_column(Text)
    correlation_id: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
