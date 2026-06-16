from datetime import date
from decimal import Decimal
from uuid import UUID

from sqlalchemy import CheckConstraint, Date, ForeignKey, ForeignKeyConstraint, Numeric, Text, Uuid
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
