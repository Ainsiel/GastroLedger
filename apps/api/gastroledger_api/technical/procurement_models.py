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


class ProcurementSupplier(Base):
    __tablename__ = "procurement_suppliers"
    __table_args__ = (CheckConstraint("status IN ('active', 'inactive')"),)

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("platform_tenants.id"))
    code: Mapped[str] = mapped_column(Text)
    name: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(Text)


class ProcurementSupplierOffer(Base):
    __tablename__ = "procurement_supplier_offers"
    __table_args__ = (
        ForeignKeyConstraint(
            ["supplier_id", "tenant_id"],
            ["procurement_suppliers.id", "procurement_suppliers.tenant_id"],
        ),
        ForeignKeyConstraint(
            ["ingredient_id", "tenant_id"],
            ["menu_ingredients.id", "menu_ingredients.tenant_id"],
        ),
        ForeignKeyConstraint(
            ["purchase_unit_id", "tenant_id"],
            ["menu_units.id", "menu_units.tenant_id"],
        ),
        CheckConstraint("price > 0"),
        CheckConstraint("currency ~ '^[A-Z]{3}$'"),
        CheckConstraint("effective_until IS NULL OR effective_until >= effective_from"),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("platform_tenants.id"))
    supplier_id: Mapped[UUID] = mapped_column(Uuid)
    ingredient_id: Mapped[UUID] = mapped_column(Uuid)
    purchase_unit_id: Mapped[UUID] = mapped_column(Uuid)
    price: Mapped[Decimal] = mapped_column(Numeric(24, 10))
    currency: Mapped[str] = mapped_column(Text)
    effective_from: Mapped[date] = mapped_column(Date)
    effective_until: Mapped[date | None] = mapped_column(Date)


class ProcurementSupplierReceipt(Base):
    __tablename__ = "procurement_supplier_receipts"
    __table_args__ = (
        ForeignKeyConstraint(
            ["supplier_id", "tenant_id"],
            ["procurement_suppliers.id", "procurement_suppliers.tenant_id"],
        ),
        ForeignKeyConstraint(
            ["warehouse_id", "tenant_id"],
            ["platform_warehouses.id", "platform_warehouses.tenant_id"],
        ),
        CheckConstraint("status IN ('accepted', 'partial', 'rejected')"),
        UniqueConstraint("tenant_id", "idempotency_key"),
        UniqueConstraint("id", "tenant_id"),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("platform_tenants.id"))
    idempotency_key: Mapped[str] = mapped_column(Text)
    order_reference: Mapped[str] = mapped_column(Text)
    supplier_id: Mapped[UUID] = mapped_column(Uuid)
    warehouse_id: Mapped[UUID] = mapped_column(Uuid)
    received_on: Mapped[date] = mapped_column(Date)
    status: Mapped[str] = mapped_column(Text)
    actor_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("platform_users.id"))
    correlation_id: Mapped[str] = mapped_column(Text)
    accepted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class ProcurementSupplierReceiptLine(Base):
    __tablename__ = "procurement_supplier_receipt_lines"
    __table_args__ = (
        ForeignKeyConstraint(
            ["receipt_id", "tenant_id"],
            ["procurement_supplier_receipts.id", "procurement_supplier_receipts.tenant_id"],
        ),
        ForeignKeyConstraint(
            ["ingredient_id", "tenant_id"],
            ["menu_ingredients.id", "menu_ingredients.tenant_id"],
        ),
        ForeignKeyConstraint(
            ["purchase_unit_id", "tenant_id"],
            ["menu_units.id", "menu_units.tenant_id"],
        ),
        CheckConstraint("ordered_quantity > 0"),
        CheckConstraint("delivered_quantity > 0"),
        CheckConstraint("accepted_quantity >= 0"),
        CheckConstraint("remaining_quantity >= 0"),
        CheckConstraint("unit_cost > 0"),
        CheckConstraint("status IN ('accepted', 'partial', 'rejected')"),
        UniqueConstraint("id", "tenant_id"),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("platform_tenants.id"))
    receipt_id: Mapped[UUID] = mapped_column(Uuid)
    ingredient_id: Mapped[UUID] = mapped_column(Uuid)
    purchase_unit_id: Mapped[UUID] = mapped_column(Uuid)
    lot_code: Mapped[str] = mapped_column(Text)
    ordered_quantity: Mapped[Decimal] = mapped_column(Numeric(24, 10))
    delivered_quantity: Mapped[Decimal] = mapped_column(Numeric(24, 10))
    accepted_quantity: Mapped[Decimal] = mapped_column(Numeric(24, 10))
    remaining_quantity: Mapped[Decimal] = mapped_column(Numeric(24, 10))
    unit_cost: Mapped[Decimal] = mapped_column(Numeric(24, 10))
    expiry_date: Mapped[date] = mapped_column(Date)
    temperature: Mapped[Decimal] = mapped_column(Numeric(12, 4))
    status: Mapped[str] = mapped_column(Text)
    rejection_reason: Mapped[str | None] = mapped_column(Text)
