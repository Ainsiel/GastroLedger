from datetime import date
from decimal import Decimal
from uuid import UUID

from sqlalchemy import CheckConstraint, Date, ForeignKey, ForeignKeyConstraint, Numeric, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from gastroledger_api.technical.platform_models import Base


class MenuUnit(Base):
    __tablename__ = "menu_units"
    __table_args__ = (CheckConstraint("dimension IN ('mass', 'volume', 'count')"),)

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("platform_tenants.id"))
    code: Mapped[str] = mapped_column(Text)
    name: Mapped[str] = mapped_column(Text)
    dimension: Mapped[str] = mapped_column(Text)


class MenuConversionFactor(Base):
    __tablename__ = "menu_conversion_factors"
    __table_args__ = (
        ForeignKeyConstraint(
            ["source_unit_id", "tenant_id"],
            ["menu_units.id", "menu_units.tenant_id"],
        ),
        ForeignKeyConstraint(
            ["target_unit_id", "tenant_id"],
            ["menu_units.id", "menu_units.tenant_id"],
        ),
        CheckConstraint("factor > 0"),
        CheckConstraint("source_unit_id <> target_unit_id"),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("platform_tenants.id"))
    source_unit_id: Mapped[UUID] = mapped_column(Uuid)
    target_unit_id: Mapped[UUID] = mapped_column(Uuid)
    factor: Mapped[Decimal] = mapped_column(Numeric(24, 10))
    effective_from: Mapped[date] = mapped_column(Date)


class MenuIngredient(Base):
    __tablename__ = "menu_ingredients"
    __table_args__ = (
        ForeignKeyConstraint(
            ["purchase_unit_id", "tenant_id"],
            ["menu_units.id", "menu_units.tenant_id"],
        ),
        ForeignKeyConstraint(
            ["consumption_unit_id", "tenant_id"],
            ["menu_units.id", "menu_units.tenant_id"],
        ),
        CheckConstraint("shelf_life_days BETWEEN 1 AND 3650"),
        CheckConstraint("critical_stock_quantity > 0"),
        CheckConstraint("status IN ('active', 'archived')"),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("platform_tenants.id"))
    code: Mapped[str] = mapped_column(Text)
    name: Mapped[str] = mapped_column(Text)
    purchase_unit_id: Mapped[UUID] = mapped_column(Uuid)
    consumption_unit_id: Mapped[UUID] = mapped_column(Uuid)
    shelf_life_days: Mapped[int]
    critical_stock_quantity: Mapped[Decimal] = mapped_column(Numeric(24, 10))
    status: Mapped[str] = mapped_column(Text)
