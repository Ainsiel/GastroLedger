from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Protocol

from gastroledger_api.modules.menu_engineering.application.catalog import (
    MenuAuthorizationDenied,
    MenuIdentity,
)
from gastroledger_api.modules.menu_engineering.domain.recipes import (
    ValidatedSubRecipeVersion,
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


class MenuRecipeStore(Protocol):
    def list_sub_recipes(self, identity: MenuIdentity) -> tuple[SubRecipeVersionView, ...]: ...

    def approve_sub_recipe_version(
        self,
        identity: MenuIdentity,
        recipe: ValidatedSubRecipeVersion,
        correlation_id: str,
    ) -> SubRecipeVersionView: ...


class MenuRecipeService:
    def __init__(self, *, store: MenuRecipeStore) -> None:
        self._store = store

    def list_sub_recipes(self, identity: MenuIdentity) -> tuple[SubRecipeVersionView, ...]:
        self._require_menu_actor(identity)
        return self._store.list_sub_recipes(identity)

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

    @staticmethod
    def _require_menu_actor(identity: MenuIdentity) -> None:
        if identity.role not in {"menu_engineer", "tenant_admin"}:
            raise MenuAuthorizationDenied
