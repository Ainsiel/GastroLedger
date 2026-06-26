from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from typing import Protocol

from gastroledger_api.modules.menu_engineering.application.catalog import (
    MenuAuthorizationDenied,
    MenuIdentity,
)
from gastroledger_api.modules.menu_engineering.domain.recipes import (
    ValidatedBranchMenuPrice,
    ValidatedMenuItemVersion,
    ValidatedSubRecipeVersion,
    validate_branch_menu_price,
    validate_menu_item_version,
    validate_sub_recipe_version,
)


@dataclass(frozen=True)
class CreateRecipeComponent:
    component_type: str
    component_id: str
    quantity: str
    unit_id: str


@dataclass(frozen=True)
class CreateSubRecipeVersion:
    name: str
    code: str
    version: str
    yield_quantity: str
    yield_unit_id: str
    effective_from: date
    components: tuple[CreateRecipeComponent, ...]


@dataclass(frozen=True)
class CreateMenuItemVersion:
    name: str
    code: str
    version: str
    yield_quantity: str
    yield_unit_id: str
    effective_from: date
    components: tuple[CreateRecipeComponent, ...]


@dataclass(frozen=True)
class CreateBranchMenuPrice:
    menu_item_version_id: str
    branch_id: str
    price: str
    currency: str
    effective_from: date


class RecipeCodeConflict(Exception):
    pass


class RecipeVersionConflict(Exception):
    pass


class RecipeGraphViolation(Exception):
    pass


class RecipeMissingCost(Exception):
    pass


@dataclass(frozen=True)
class RecipeComponentView:
    component_type: str
    component_id: str
    quantity: Decimal
    unit_id: str


@dataclass(frozen=True)
class CostSnapshotView:
    total_cost: Decimal
    status: str


@dataclass(frozen=True)
class CostProjectionView:
    status: str
    updated_at: datetime
    last_error: str | None


@dataclass(frozen=True)
class BranchMenuMarginView:
    branch_price_id: str
    menu_item_version_id: str
    branch_id: str
    price: Decimal
    currency: str
    theoretical_cost: Decimal
    contribution_margin: Decimal
    margin_percent: Decimal
    suggested_price: Decimal
    effective_from: date


@dataclass(frozen=True)
class SubRecipeVersionView:
    recipe_id: str
    recipe_version_id: str
    name: str
    code: str
    version: str
    yield_quantity: Decimal
    yield_unit_id: str
    effective_from: date
    status: str
    is_active: bool
    components: tuple[RecipeComponentView, ...]
    cost_snapshot: CostSnapshotView
    cost_projection: CostProjectionView | None = None


@dataclass(frozen=True)
class MenuItemVersionView:
    recipe_id: str
    recipe_version_id: str
    name: str
    code: str
    version: str
    yield_quantity: Decimal
    yield_unit_id: str
    effective_from: date
    status: str
    is_active: bool
    components: tuple[RecipeComponentView, ...]
    cost_snapshot: CostSnapshotView
    branch_margins: tuple[BranchMenuMarginView, ...]
    cost_projection: CostProjectionView | None = None


class MenuRecipeStore(Protocol):
    def list_sub_recipes(self, identity: MenuIdentity) -> tuple[SubRecipeVersionView, ...]: ...

    def list_menu_items(self, identity: MenuIdentity) -> tuple[MenuItemVersionView, ...]: ...

    def approve_sub_recipe_version(
        self,
        identity: MenuIdentity,
        recipe: ValidatedSubRecipeVersion,
        correlation_id: str,
    ) -> SubRecipeVersionView: ...

    def approve_menu_item_version(
        self,
        identity: MenuIdentity,
        recipe: ValidatedMenuItemVersion,
        correlation_id: str,
    ) -> MenuItemVersionView: ...

    def create_branch_price(
        self,
        identity: MenuIdentity,
        price: ValidatedBranchMenuPrice,
        correlation_id: str,
    ) -> BranchMenuMarginView: ...


class MenuRecipeService:
    def __init__(self, *, store: MenuRecipeStore) -> None:
        self._store = store

    def list_sub_recipes(self, identity: MenuIdentity) -> tuple[SubRecipeVersionView, ...]:
        self._require_menu_actor(identity)
        return self._store.list_sub_recipes(identity)

    def list_menu_items(self, identity: MenuIdentity) -> tuple[MenuItemVersionView, ...]:
        self._require_menu_actor(identity)
        return self._store.list_menu_items(identity)

    def approve_sub_recipe_version(
        self,
        identity: MenuIdentity,
        command: CreateSubRecipeVersion,
        *,
        correlation_id: str,
    ) -> SubRecipeVersionView:
        self._require_menu_actor(identity)
        recipe = validate_sub_recipe_version(
            name=command.name,
            code=command.code,
            version=command.version,
            yield_quantity=command.yield_quantity,
            yield_unit_id=command.yield_unit_id,
            effective_from=command.effective_from,
            components=command.components,
        )
        return self._store.approve_sub_recipe_version(identity, recipe, correlation_id)

    def approve_menu_item_version(
        self,
        identity: MenuIdentity,
        command: CreateMenuItemVersion,
        *,
        correlation_id: str,
    ) -> MenuItemVersionView:
        self._require_menu_actor(identity)
        recipe = validate_menu_item_version(
            name=command.name,
            code=command.code,
            version=command.version,
            yield_quantity=command.yield_quantity,
            yield_unit_id=command.yield_unit_id,
            effective_from=command.effective_from,
            components=command.components,
        )
        return self._store.approve_menu_item_version(identity, recipe, correlation_id)

    def create_branch_price(
        self,
        identity: MenuIdentity,
        command: CreateBranchMenuPrice,
        *,
        correlation_id: str,
    ) -> BranchMenuMarginView:
        self._require_menu_actor(identity)
        price = validate_branch_menu_price(
            menu_item_version_id=command.menu_item_version_id,
            branch_id=command.branch_id,
            price=command.price,
            currency=command.currency,
            effective_from=command.effective_from,
        )
        return self._store.create_branch_price(identity, price, correlation_id)

    @staticmethod
    def _require_menu_actor(identity: MenuIdentity) -> None:
        if identity.role not in {"menu_engineer", "tenant_admin"}:
            raise MenuAuthorizationDenied
