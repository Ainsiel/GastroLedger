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


class MenuRecipe(Base):
    __tablename__ = "menu_recipes"
    __table_args__ = (
        CheckConstraint("recipe_type IN ('sub_recipe', 'menu_item')"),
        UniqueConstraint("tenant_id", "code"),
        UniqueConstraint("id", "tenant_id"),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("platform_tenants.id"))
    code: Mapped[str] = mapped_column(Text)
    name: Mapped[str] = mapped_column(Text)
    recipe_type: Mapped[str] = mapped_column(Text)


class MenuRecipeVersion(Base):
    __tablename__ = "menu_recipe_versions"
    __table_args__ = (
        ForeignKeyConstraint(
            ["recipe_id", "tenant_id"],
            ["menu_recipes.id", "menu_recipes.tenant_id"],
        ),
        ForeignKeyConstraint(
            ["yield_unit_id", "tenant_id"],
            ["menu_units.id", "menu_units.tenant_id"],
        ),
        CheckConstraint("yield_quantity > 0"),
        CheckConstraint("status IN ('approved', 'scheduled')"),
        UniqueConstraint("tenant_id", "recipe_id", "version"),
        UniqueConstraint("id", "tenant_id"),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("platform_tenants.id"))
    recipe_id: Mapped[UUID] = mapped_column(Uuid)
    version: Mapped[str] = mapped_column(Text)
    yield_quantity: Mapped[Decimal] = mapped_column(Numeric(24, 10))
    yield_unit_id: Mapped[UUID] = mapped_column(Uuid)
    effective_from: Mapped[date] = mapped_column(Date)
    status: Mapped[str] = mapped_column(Text)
    approved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class MenuRecipeComponent(Base):
    __tablename__ = "menu_recipe_components"
    __table_args__ = (
        ForeignKeyConstraint(
            ["recipe_version_id", "tenant_id"],
            ["menu_recipe_versions.id", "menu_recipe_versions.tenant_id"],
        ),
        ForeignKeyConstraint(
            ["ingredient_id", "tenant_id"],
            ["menu_ingredients.id", "menu_ingredients.tenant_id"],
        ),
        ForeignKeyConstraint(
            ["component_recipe_id", "tenant_id"],
            ["menu_recipes.id", "menu_recipes.tenant_id"],
        ),
        ForeignKeyConstraint(
            ["unit_id", "tenant_id"],
            ["menu_units.id", "menu_units.tenant_id"],
        ),
        CheckConstraint("component_type IN ('ingredient', 'sub_recipe')"),
        CheckConstraint("quantity > 0"),
        CheckConstraint(
            "(component_type = 'ingredient' "
            "AND ingredient_id IS NOT NULL "
            "AND component_recipe_id IS NULL) OR "
            "(component_type = 'sub_recipe' "
            "AND ingredient_id IS NULL "
            "AND component_recipe_id IS NOT NULL)"
        ),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("platform_tenants.id"))
    recipe_version_id: Mapped[UUID] = mapped_column(Uuid)
    component_type: Mapped[str] = mapped_column(Text)
    ingredient_id: Mapped[UUID | None] = mapped_column(Uuid)
    component_recipe_id: Mapped[UUID | None] = mapped_column(Uuid)
    quantity: Mapped[Decimal] = mapped_column(Numeric(24, 10))
    unit_id: Mapped[UUID] = mapped_column(Uuid)


class MenuCostSnapshot(Base):
    __tablename__ = "menu_cost_snapshots"
    __table_args__ = (
        ForeignKeyConstraint(
            ["recipe_version_id", "tenant_id"],
            ["menu_recipe_versions.id", "menu_recipe_versions.tenant_id"],
        ),
        CheckConstraint("total_cost >= 0"),
        CheckConstraint("status IN ('current', 'missing_cost')"),
        UniqueConstraint("tenant_id", "recipe_version_id"),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("platform_tenants.id"))
    recipe_version_id: Mapped[UUID] = mapped_column(Uuid)
    as_of: Mapped[date] = mapped_column(Date)
    total_cost: Mapped[Decimal] = mapped_column(Numeric(24, 10))
    status: Mapped[str] = mapped_column(Text)


class MenuItemBranchPrice(Base):
    __tablename__ = "menu_item_branch_prices"
    __table_args__ = (
        ForeignKeyConstraint(
            ["recipe_version_id", "tenant_id"],
            ["menu_recipe_versions.id", "menu_recipe_versions.tenant_id"],
        ),
        ForeignKeyConstraint(
            ["branch_id", "tenant_id"],
            ["platform_branches.id", "platform_branches.tenant_id"],
        ),
        CheckConstraint("price > 0"),
        CheckConstraint("currency ~ '^[A-Z]{3}$'"),
        UniqueConstraint("tenant_id", "recipe_version_id", "branch_id", "effective_from"),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("platform_tenants.id"))
    recipe_version_id: Mapped[UUID] = mapped_column(Uuid)
    branch_id: Mapped[UUID] = mapped_column(Uuid)
    price: Mapped[Decimal] = mapped_column(Numeric(24, 10))
    currency: Mapped[str] = mapped_column(Text)
    effective_from: Mapped[date] = mapped_column(Date)
