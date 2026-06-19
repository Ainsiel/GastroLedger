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
        UniqueConstraint("tenant_id", "source_receipt_id"),
        UniqueConstraint("id", "tenant_id"),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("platform_tenants.id"))
    warehouse_id: Mapped[UUID] = mapped_column(Uuid)
    source_receipt_id: Mapped[UUID] = mapped_column(Uuid)
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
        CheckConstraint("unit_cost > 0"),
        UniqueConstraint("tenant_id", "warehouse_id", "lot_code"),
        UniqueConstraint("id", "tenant_id"),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("platform_tenants.id"))
    warehouse_id: Mapped[UUID] = mapped_column(Uuid)
    ingredient_id: Mapped[UUID] = mapped_column(Uuid)
    unit_id: Mapped[UUID] = mapped_column(Uuid)
    lot_code: Mapped[str] = mapped_column(Text)
    expiry_date: Mapped[date] = mapped_column(Date)
    unit_cost: Mapped[Decimal] = mapped_column(Numeric(24, 10))
    source_receipt_line_id: Mapped[UUID] = mapped_column(Uuid)
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
