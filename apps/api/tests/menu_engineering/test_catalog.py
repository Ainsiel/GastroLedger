from datetime import date
from decimal import Decimal

import pytest

from gastroledger_api.modules.menu_engineering.public import (
    ArchiveIngredient,
    CreateBranchMenuPrice,
    CreateConversionFactor,
    CreateIngredient,
    CreateMenuItemVersion,
    CreateRecipeComponent,
    CreateSubRecipeVersion,
    CreateUnit,
    IngredientArchived,
    MenuAuthorizationDenied,
    MenuCatalogService,
    MenuIdentity,
    MenuRecipeService,
    MenuValidationError,
    RecipeGraphViolation,
    RecipeMissingCost,
    UnitConversionUnavailable,
    UnitDimensionMismatch,
    validate_conversion_factor,
    validate_ingredient,
    validate_menu_item_version,
    validate_sub_recipe_version,
    validate_unit,
)


def test_unit_and_ingredient_inputs_are_normalized() -> None:
    unit = validate_unit(name="  Kilogram  ", code=" kg ", dimension="MASS")
    ingredient = validate_ingredient(
        name="  Flour  ",
        code=" flour-all-purpose ",
        purchase_unit_id="unit-purchase",
        consumption_unit_id="unit-consumption",
        shelf_life_days=180,
        critical_stock_quantity="12.500",
    )

    assert (unit.name, unit.code, unit.dimension) == ("Kilogram", "KG", "mass")
    assert ingredient.name == "Flour"
    assert ingredient.code == "FLOUR-ALL-PURPOSE"
    assert ingredient.critical_stock_quantity == Decimal("12.500")


def test_non_positive_conversion_and_unknown_dimension_are_rejected() -> None:
    with pytest.raises(MenuValidationError) as error:
        validate_unit(name="Bottle", code="bottle", dimension="currency")

    assert [(detail.field, detail.code) for detail in error.value.details] == [
        ("dimension", "unsupported")
    ]

    with pytest.raises(MenuValidationError) as conversion_error:
        validate_conversion_factor(
            source_unit_id="unit-a",
            target_unit_id="unit-b",
            factor="0",
            effective_from=date(2026, 6, 16),
        )

    assert [(detail.field, detail.code) for detail in conversion_error.value.details] == [
        ("factor", "positive_required")
    ]


class RecordingMenuStore:
    def __init__(self) -> None:
        self.units: list[object] = []
        self.conversions: list[object] = []
        self.ingredients: list[object] = []
        self.archived: list[str] = []
        self.source_dimension = "mass"
        self.target_dimension = "mass"
        self.active_conversion_exists = True
        self.ingredient_archived = False

    def list_units(self, _identity: MenuIdentity) -> tuple[object, ...]:
        return tuple(self.units)

    def create_unit(self, _identity: MenuIdentity, unit: object, _correlation_id: str) -> object:
        self.units.append(unit)
        return unit

    def create_conversion_factor(
        self,
        _identity: MenuIdentity,
        conversion: object,
        _correlation_id: str,
    ) -> object:
        self.conversions.append(conversion)
        return conversion

    def convert_quantity(
        self,
        _identity: MenuIdentity,
        source_unit_id: str,
        target_unit_id: str,
        quantity: Decimal,
        as_of: date,
    ) -> object:
        del as_of
        if not self.active_conversion_exists:
            raise UnitConversionUnavailable
        return {
            "quantity": quantity * Decimal("1000"),
            "target_unit_id": target_unit_id,
        }

    def list_ingredients(self, _identity: MenuIdentity) -> tuple[object, ...]:
        return tuple(self.ingredients)

    def create_ingredient(
        self,
        _identity: MenuIdentity,
        ingredient: object,
        _correlation_id: str,
    ) -> object:
        if self.source_dimension != self.target_dimension:
            raise UnitDimensionMismatch
        if not self.active_conversion_exists:
            raise UnitConversionUnavailable
        self.ingredients.append(ingredient)
        return ingredient

    def archive_ingredient(
        self,
        _identity: MenuIdentity,
        ingredient_id: str,
        _correlation_id: str,
    ) -> object:
        if self.ingredient_archived:
            raise IngredientArchived
        self.archived.append(ingredient_id)
        return {"ingredient_id": ingredient_id, "status": "archived"}


def admin_identity() -> MenuIdentity:
    return MenuIdentity(
        tenant_id="tenant-1",
        actor_id="actor-1",
        role="tenant_admin",
    )


def test_menu_engineer_records_precise_conversion_and_uses_current_factor() -> None:
    store = RecordingMenuStore()
    service = MenuCatalogService(store=store)

    unit = service.create_unit(
        admin_identity(),
        CreateUnit(name="  Gram  ", code=" g ", dimension="mass"),
        correlation_id="unit-1",
    )
    conversion = service.create_conversion_factor(
        admin_identity(),
        CreateConversionFactor(
            source_unit_id="unit-kg",
            target_unit_id="unit-g",
            factor="1000.0000",
            effective_from=date(2026, 6, 16),
        ),
        correlation_id="conversion-1",
    )
    converted = service.convert_quantity(
        admin_identity(),
        source_unit_id="unit-kg",
        target_unit_id="unit-g",
        quantity=Decimal("1.25"),
        as_of=date(2026, 6, 16),
    )

    assert getattr(unit, "code") == "G"
    assert getattr(conversion, "factor") == Decimal("1000.0000")
    assert converted["quantity"] == Decimal("1250.00")


def test_incompatible_or_missing_unit_mapping_blocks_ingredient_creation() -> None:
    store = RecordingMenuStore()
    store.source_dimension = "mass"
    store.target_dimension = "volume"
    service = MenuCatalogService(store=store)

    with pytest.raises(UnitDimensionMismatch):
        service.create_ingredient(
            admin_identity(),
            CreateIngredient(
                name="Flour",
                code="FLOUR",
                purchase_unit_id="unit-kg",
                consumption_unit_id="unit-liter",
                shelf_life_days=180,
                critical_stock_quantity="10",
            ),
            correlation_id="ingredient-1",
        )

    store.source_dimension = "mass"
    store.target_dimension = "mass"
    store.active_conversion_exists = False

    with pytest.raises(UnitConversionUnavailable):
        service.create_ingredient(
            admin_identity(),
            CreateIngredient(
                name="Flour",
                code="FLOUR",
                purchase_unit_id="unit-kg",
                consumption_unit_id="unit-g",
                shelf_life_days=180,
                critical_stock_quantity="10",
            ),
            correlation_id="ingredient-2",
        )

    assert store.ingredients == []


def test_non_menu_actor_cannot_mutate_catalog() -> None:
    store = RecordingMenuStore()
    service = MenuCatalogService(store=store)

    with pytest.raises(MenuAuthorizationDenied):
        service.create_unit(
            MenuIdentity(tenant_id="tenant-1", actor_id="actor-1", role="operator"),
            CreateUnit(name="Gram", code="G", dimension="mass"),
            correlation_id="unit-1",
        )

    assert store.units == []


def test_archived_ingredient_is_reported_as_not_available_for_new_use() -> None:
    store = RecordingMenuStore()
    service = MenuCatalogService(store=store)

    archived = service.archive_ingredient(
        admin_identity(),
        ArchiveIngredient(ingredient_id="ingredient-1"),
        correlation_id="archive-1",
    )

    assert archived["status"] == "archived"
    assert store.archived == ["ingredient-1"]


class RecordingRecipeStore:
    def __init__(self) -> None:
        self.approved: list[object] = []
        self.menu_items: list[object] = []
        self.branch_prices: list[object] = []
        self.reject_graph = False
        self.reject_missing_cost = False

    def list_sub_recipes(self, _identity: MenuIdentity) -> tuple[object, ...]:
        return tuple(self.approved)

    def list_menu_items(self, _identity: MenuIdentity) -> tuple[object, ...]:
        return tuple(self.menu_items)

    def approve_sub_recipe_version(
        self,
        _identity: MenuIdentity,
        recipe: object,
        _correlation_id: str,
    ) -> object:
        if self.reject_graph:
            raise RecipeGraphViolation("cycle")
        self.approved.append(recipe)
        return {
            "recipe_id": "recipe-1",
            "recipe_version_id": "version-1",
            "code": recipe.code,
            "name": recipe.name,
            "version": recipe.version,
            "status": "approved",
            "is_active": True,
            "yield_quantity": recipe.yield_quantity,
            "yield_unit_id": recipe.yield_unit_id,
            "effective_from": recipe.effective_from,
            "components": recipe.components,
            "cost_snapshot": {"total_cost": recipe.yield_quantity, "status": "current"},
        }

    def approve_menu_item_version(
        self,
        _identity: MenuIdentity,
        recipe: object,
        _correlation_id: str,
    ) -> object:
        if self.reject_missing_cost:
            raise RecipeMissingCost
        view = {
            "recipe_id": "menu-item-1",
            "recipe_version_id": "menu-item-version-1",
            "code": recipe.code,
            "name": recipe.name,
            "version": recipe.version,
            "status": "approved",
            "is_active": True,
            "yield_quantity": recipe.yield_quantity,
            "yield_unit_id": recipe.yield_unit_id,
            "effective_from": recipe.effective_from,
            "components": recipe.components,
            "cost_snapshot": {"total_cost": recipe.yield_quantity, "status": "current"},
            "branch_margins": tuple(),
        }
        self.menu_items.append(view)
        return view

    def create_branch_price(
        self,
        _identity: MenuIdentity,
        price: object,
        _correlation_id: str,
    ) -> object:
        view = {
            "branch_price_id": "branch-price-1",
            "menu_item_version_id": price.menu_item_version_id,
            "branch_id": price.branch_id,
            "price": price.price,
            "currency": price.currency,
            "theoretical_cost": Decimal("4"),
            "contribution_margin": price.price - Decimal("4"),
            "margin_percent": Decimal("60"),
            "suggested_price": Decimal("12"),
            "effective_from": price.effective_from,
        }
        self.branch_prices.append(view)
        return view


def test_sub_recipe_version_validation_normalizes_and_requires_positive_values() -> None:
    version = validate_sub_recipe_version(
        name="  Sofrito base  ",
        code=" sofrito-base ",
        version=" v1 ",
        yield_quantity="2.5",
        yield_unit_id="unit-kg",
        effective_from=date(2026, 6, 19),
        components=(
            CreateRecipeComponent(
                component_type="ingredient",
                component_id="ingredient-onion",
                quantity="1.25",
                unit_id="unit-kg",
            ),
        ),
    )

    assert version.name == "Sofrito base"
    assert version.code == "SOFRITO-BASE"
    assert version.yield_quantity == Decimal("2.5")
    assert version.components[0].quantity == Decimal("1.25")

    with pytest.raises(MenuValidationError) as error:
        validate_sub_recipe_version(
            name="Sofrito base",
            code="sofrito-base",
            version="v1",
            yield_quantity="0",
            yield_unit_id="unit-kg",
            effective_from=date(2026, 6, 19),
            components=(),
        )

    assert ("yieldQuantity", "positive_required") in [
        (detail.field, detail.code) for detail in error.value.details
    ]
    assert ("components", "required") in [
        (detail.field, detail.code) for detail in error.value.details
    ]


def test_menu_item_version_validation_allows_sub_recipe_components() -> None:
    version = validate_menu_item_version(
        name="  Lunch Bowl  ",
        code=" lunch-bowl ",
        version=" v1 ",
        yield_quantity="1",
        yield_unit_id="unit-serving",
        effective_from=date(2026, 6, 19),
        components=(
            CreateRecipeComponent(
                component_type="sub_recipe",
                component_id="sub-recipe-1",
                quantity="0.25",
                unit_id="unit-kg",
            ),
        ),
    )

    assert version.name == "Lunch Bowl"
    assert version.code == "LUNCH-BOWL"
    assert version.components[0].component_type == "sub_recipe"


def test_menu_engineer_approves_sub_recipe_version_and_surfaces_graph_rejection() -> None:
    store = RecordingRecipeStore()
    service = MenuRecipeService(store=store)

    approved = service.approve_sub_recipe_version(
        admin_identity(),
        CreateSubRecipeVersion(
            name="Sofrito base",
            code="sofrito-base",
            version="v1",
            yield_quantity="2",
            yield_unit_id="unit-kg",
            effective_from=date(2026, 6, 19),
            components=(
                CreateRecipeComponent(
                    component_type="ingredient",
                    component_id="ingredient-onion",
                    quantity="1",
                    unit_id="unit-kg",
                ),
            ),
        ),
        correlation_id="recipe-approve",
    )

    assert approved["code"] == "SOFRITO-BASE"
    assert approved["status"] == "approved"

    store.reject_graph = True
    with pytest.raises(RecipeGraphViolation):
        service.approve_sub_recipe_version(
            admin_identity(),
            CreateSubRecipeVersion(
                name="Nested sauce",
                code="nested-sauce",
                version="v1",
                yield_quantity="1",
                yield_unit_id="unit-kg",
                effective_from=date(2026, 6, 19),
                components=(
                    CreateRecipeComponent(
                        component_type="sub_recipe",
                        component_id="recipe-1",
                        quantity="1",
                        unit_id="unit-kg",
                    ),
                ),
            ),
            correlation_id="recipe-cycle",
        )


def test_menu_engineer_approves_menu_item_and_records_branch_margin() -> None:
    store = RecordingRecipeStore()
    service = MenuRecipeService(store=store)

    approved = service.approve_menu_item_version(
        admin_identity(),
        CreateMenuItemVersion(
            name="Lunch Bowl",
            code="lunch-bowl",
            version="v1",
            yield_quantity="1",
            yield_unit_id="unit-serving",
            effective_from=date(2026, 6, 19),
            components=(
                CreateRecipeComponent(
                    component_type="sub_recipe",
                    component_id="sub-recipe-1",
                    quantity="1",
                    unit_id="unit-serving",
                ),
            ),
        ),
        correlation_id="menu-item-approve",
    )
    margin = service.create_branch_price(
        admin_identity(),
        CreateBranchMenuPrice(
            menu_item_version_id="menu-item-version-1",
            branch_id="branch-1",
            price="10",
            currency="usd",
            effective_from=date(2026, 6, 19),
        ),
        correlation_id="branch-price",
    )

    assert approved["code"] == "LUNCH-BOWL"
    assert approved["status"] == "approved"
    assert margin["currency"] == "USD"
    assert margin["contribution_margin"] == Decimal("6")

    store.reject_missing_cost = True
    with pytest.raises(RecipeMissingCost):
        service.approve_menu_item_version(
            admin_identity(),
            CreateMenuItemVersion(
                name="No cost bowl",
                code="no-cost-bowl",
                version="v1",
                yield_quantity="1",
                yield_unit_id="unit-serving",
                effective_from=date(2026, 6, 19),
                components=(
                    CreateRecipeComponent(
                        component_type="ingredient",
                        component_id="ingredient-missing",
                        quantity="1",
                        unit_id="unit-serving",
                    ),
                ),
            ),
            correlation_id="menu-item-missing-cost",
        )
