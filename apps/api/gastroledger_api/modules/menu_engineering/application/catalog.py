from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Protocol

from gastroledger_api.application.identifiers import ActorId, TenantId
from gastroledger_api.modules.menu_engineering.domain.catalog import (
    ValidatedConversionFactor,
    ValidatedIngredient,
    ValidatedUnit,
    validate_conversion_factor,
    validate_ingredient,
    validate_unit,
)


@dataclass(frozen=True)
class MenuIdentity:
    tenant_id: TenantId
    actor_id: ActorId
    role: str


@dataclass(frozen=True)
class CreateUnit:
    name: str
    code: str
    dimension: str


@dataclass(frozen=True)
class CreateConversionFactor:
    source_unit_id: str
    target_unit_id: str
    factor: str
    effective_from: date


@dataclass(frozen=True)
class CreateIngredient:
    name: str
    code: str
    purchase_unit_id: str
    consumption_unit_id: str
    shelf_life_days: int
    critical_stock_quantity: str


@dataclass(frozen=True)
class ArchiveIngredient:
    ingredient_id: str


class MenuAuthorizationDenied(Exception):
    pass


class MenuCodeConflict(Exception):
    pass


class IngredientCodeConflict(MenuCodeConflict):
    pass


class MenuNotFound(Exception):
    pass


class UnitDimensionMismatch(Exception):
    pass


class UnitConversionUnavailable(Exception):
    pass


class IngredientArchived(Exception):
    pass


@dataclass(frozen=True)
class ConversionFactorView:
    conversion_factor_id: str
    source_unit_id: str
    target_unit_id: str
    factor: Decimal
    effective_from: date


@dataclass(frozen=True)
class UnitView:
    unit_id: str
    name: str
    code: str
    dimension: str
    conversions: tuple[ConversionFactorView, ...] = ()


@dataclass(frozen=True)
class IngredientView:
    ingredient_id: str
    name: str
    code: str
    purchase_unit_id: str
    consumption_unit_id: str
    shelf_life_days: int
    critical_stock_quantity: Decimal
    status: str
    available_for_new_use: bool


@dataclass(frozen=True)
class UnitConversionResult:
    quantity: Decimal
    target_unit_id: str


class MenuCatalogStore(Protocol):
    def list_units(self, identity: MenuIdentity) -> tuple[UnitView, ...]: ...

    def create_unit(
        self,
        identity: MenuIdentity,
        unit: ValidatedUnit,
        correlation_id: str,
    ) -> UnitView: ...

    def create_conversion_factor(
        self,
        identity: MenuIdentity,
        conversion: ValidatedConversionFactor,
        correlation_id: str,
    ) -> ConversionFactorView: ...

    def convert_quantity(
        self,
        identity: MenuIdentity,
        source_unit_id: str,
        target_unit_id: str,
        quantity: Decimal,
        as_of: date,
    ) -> UnitConversionResult: ...

    def list_ingredients(self, identity: MenuIdentity) -> tuple[IngredientView, ...]: ...

    def create_ingredient(
        self,
        identity: MenuIdentity,
        ingredient: ValidatedIngredient,
        correlation_id: str,
    ) -> IngredientView: ...

    def archive_ingredient(
        self,
        identity: MenuIdentity,
        ingredient_id: str,
        correlation_id: str,
    ) -> IngredientView: ...


class MenuCatalogService:
    def __init__(self, *, store: MenuCatalogStore) -> None:
        self._store = store

    def list_units(self, identity: MenuIdentity) -> tuple[UnitView, ...]:
        self._require_menu_actor(identity)
        return self._store.list_units(identity)

    def create_unit(
        self,
        identity: MenuIdentity,
        command: CreateUnit,
        *,
        correlation_id: str,
    ) -> UnitView:
        self._require_menu_actor(identity)
        unit = validate_unit(
            name=command.name,
            code=command.code,
            dimension=command.dimension,
        )
        return self._store.create_unit(identity, unit, correlation_id)

    def create_conversion_factor(
        self,
        identity: MenuIdentity,
        command: CreateConversionFactor,
        *,
        correlation_id: str,
    ) -> ConversionFactorView:
        self._require_menu_actor(identity)
        conversion = validate_conversion_factor(
            source_unit_id=command.source_unit_id,
            target_unit_id=command.target_unit_id,
            factor=command.factor,
            effective_from=command.effective_from,
        )
        return self._store.create_conversion_factor(identity, conversion, correlation_id)

    def convert_quantity(
        self,
        identity: MenuIdentity,
        *,
        source_unit_id: str,
        target_unit_id: str,
        quantity: Decimal,
        as_of: date,
    ) -> UnitConversionResult:
        self._require_menu_actor(identity)
        return self._store.convert_quantity(
            identity,
            source_unit_id,
            target_unit_id,
            quantity,
            as_of,
        )

    def list_ingredients(self, identity: MenuIdentity) -> tuple[IngredientView, ...]:
        self._require_menu_actor(identity)
        return self._store.list_ingredients(identity)

    def create_ingredient(
        self,
        identity: MenuIdentity,
        command: CreateIngredient,
        *,
        correlation_id: str,
    ) -> IngredientView:
        self._require_menu_actor(identity)
        ingredient = validate_ingredient(
            name=command.name,
            code=command.code,
            purchase_unit_id=command.purchase_unit_id,
            consumption_unit_id=command.consumption_unit_id,
            shelf_life_days=command.shelf_life_days,
            critical_stock_quantity=command.critical_stock_quantity,
        )
        return self._store.create_ingredient(identity, ingredient, correlation_id)

    def archive_ingredient(
        self,
        identity: MenuIdentity,
        command: ArchiveIngredient,
        *,
        correlation_id: str,
    ) -> IngredientView:
        self._require_menu_actor(identity)
        return self._store.archive_ingredient(
            identity,
            command.ingredient_id.strip(),
            correlation_id,
        )

    @staticmethod
    def _require_menu_actor(identity: MenuIdentity) -> None:
        if identity.role not in {"menu_engineer", "tenant_admin"}:
            raise MenuAuthorizationDenied
