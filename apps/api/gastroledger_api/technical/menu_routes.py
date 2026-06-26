import os
from datetime import date, datetime
from uuid import UUID, uuid4

import psycopg
from fastapi import APIRouter, Security
from fastapi.security import APIKeyCookie
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.exc import SQLAlchemyError

from gastroledger_api.modules.menu_engineering.public import (
    ArchiveIngredient,
    BranchMenuMarginView,
    ConversionFactorView,
    CostProjectionView,
    CostSnapshotView,
    CreateBranchMenuPrice,
    CreateConversionFactor,
    CreateIngredient,
    CreateMenuItemVersion,
    CreateRecipeComponent,
    CreateSubRecipeVersion,
    CreateUnit,
    IngredientArchived,
    IngredientCodeConflict,
    IngredientView,
    MenuAuthorizationDenied,
    MenuCatalogService,
    MenuCodeConflict,
    MenuIdentity,
    MenuItemVersionView,
    MenuNotFound,
    MenuRecipeService,
    MenuValidationError,
    RecipeCodeConflict,
    RecipeComponentView,
    RecipeGraphViolation,
    RecipeMissingCost,
    RecipeVersionConflict,
    SubRecipeVersionView,
    UnitConversionUnavailable,
    UnitDimensionMismatch,
    UnitView,
)
from gastroledger_api.modules.platform_organization.public import AuthenticationRequired
from gastroledger_api.technical.postgres_menu import PostgresMenuCatalogStore
from gastroledger_api.technical.postgres_platform import PostgresPlatformStore
from gastroledger_api.technical.problems import ApiProblem, problem_response

SESSION_COOKIE = "gl_session"
session_cookie = APIKeyCookie(
    name=SESSION_COOKIE,
    auto_error=False,
    description="Opaque local session cookie issued after tenant registration or login.",
)

MENU_RESPONSES = {
    401: {"model": ApiProblem, "description": "A valid local session is required."},
    403: {"model": ApiProblem, "description": "Menu Engineering access is required."},
    404: {"model": ApiProblem, "description": "The scoped menu resource is not visible."},
    409: {"model": ApiProblem, "description": "The menu catalog command conflicts."},
    422: {"model": ApiProblem, "description": "The menu catalog input is invalid."},
    500: {"model": ApiProblem, "description": "The command could not be completed."},
}


class UnitRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=120)
    code: str = Field(min_length=1, max_length=63)
    dimension: str = Field(min_length=1, max_length=20)


class ConversionFactorRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    sourceUnitId: str = Field(min_length=1)
    targetUnitId: str = Field(min_length=1)
    factor: str = Field(min_length=1, max_length=50)
    effectiveFrom: date


class IngredientRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=120)
    code: str = Field(min_length=1, max_length=63)
    purchaseUnitId: str = Field(min_length=1)
    consumptionUnitId: str = Field(min_length=1)
    shelfLifeDays: int = Field(strict=True, ge=1, le=3650)
    criticalStockQuantity: str = Field(min_length=1, max_length=50)


class RecipeComponentRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    componentType: str = Field(min_length=1, max_length=20)
    componentId: str = Field(min_length=1)
    quantity: str = Field(min_length=1, max_length=50)
    unitId: str = Field(min_length=1)


class SubRecipeVersionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=120)
    code: str = Field(min_length=1, max_length=63)
    version: str = Field(min_length=1, max_length=40)
    yieldQuantity: str = Field(min_length=1, max_length=50)
    yieldUnitId: str = Field(min_length=1)
    effectiveFrom: date
    components: list[RecipeComponentRequest] = Field(min_length=1)


class MenuItemVersionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=120)
    code: str = Field(min_length=1, max_length=63)
    version: str = Field(min_length=1, max_length=40)
    yieldQuantity: str = Field(min_length=1, max_length=50)
    yieldUnitId: str = Field(min_length=1)
    effectiveFrom: date
    components: list[RecipeComponentRequest] = Field(min_length=1)


class BranchMenuPriceRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    branchId: str = Field(min_length=1)
    price: str = Field(min_length=1, max_length=50)
    currency: str = Field(min_length=3, max_length=3)
    effectiveFrom: date


class ConversionFactorResponse(BaseModel):
    conversionFactorId: str
    sourceUnitId: str
    targetUnitId: str
    factor: str
    effectiveFrom: date


class UnitResponse(BaseModel):
    unitId: str
    name: str
    code: str
    dimension: str
    conversions: list[ConversionFactorResponse]


class IngredientResponse(BaseModel):
    ingredientId: str
    name: str
    code: str
    purchaseUnitId: str
    consumptionUnitId: str
    shelfLifeDays: int
    criticalStockQuantity: str
    status: str
    availableForNewUse: bool


class RecipeComponentResponse(BaseModel):
    componentType: str
    componentId: str
    quantity: str
    unitId: str


class CostSnapshotResponse(BaseModel):
    totalCost: str
    status: str


class CostProjectionResponse(BaseModel):
    status: str
    updatedAt: datetime
    lastError: str | None = None


class SubRecipeVersionResponse(BaseModel):
    recipeId: str
    recipeVersionId: str
    name: str
    code: str
    version: str
    yieldQuantity: str
    yieldUnitId: str
    effectiveFrom: date
    status: str
    isActive: bool
    components: list[RecipeComponentResponse]
    costSnapshot: CostSnapshotResponse
    costProjection: CostProjectionResponse | None = None


class BranchMenuMarginResponse(BaseModel):
    branchPriceId: str
    menuItemVersionId: str
    branchId: str
    price: str
    currency: str
    theoreticalCost: str
    contributionMargin: str
    marginPercent: str
    suggestedPrice: str
    effectiveFrom: date


class MenuItemVersionResponse(BaseModel):
    recipeId: str
    recipeVersionId: str
    name: str
    code: str
    version: str
    yieldQuantity: str
    yieldUnitId: str
    effectiveFrom: date
    status: str
    isActive: bool
    components: list[RecipeComponentResponse]
    costSnapshot: CostSnapshotResponse
    branchMargins: list[BranchMenuMarginResponse]
    costProjection: CostProjectionResponse | None = None


def conversion_response(conversion: ConversionFactorView) -> ConversionFactorResponse:
    return ConversionFactorResponse(
        conversionFactorId=conversion.conversion_factor_id,
        sourceUnitId=conversion.source_unit_id,
        targetUnitId=conversion.target_unit_id,
        factor=format(conversion.factor.normalize(), "f"),
        effectiveFrom=conversion.effective_from,
    )


def unit_response(unit: UnitView) -> UnitResponse:
    return UnitResponse(
        unitId=unit.unit_id,
        name=unit.name,
        code=unit.code,
        dimension=unit.dimension,
        conversions=[conversion_response(conversion) for conversion in unit.conversions],
    )


def ingredient_response(ingredient: IngredientView) -> IngredientResponse:
    return IngredientResponse(
        ingredientId=ingredient.ingredient_id,
        name=ingredient.name,
        code=ingredient.code,
        purchaseUnitId=ingredient.purchase_unit_id,
        consumptionUnitId=ingredient.consumption_unit_id,
        shelfLifeDays=ingredient.shelf_life_days,
        criticalStockQuantity=format(ingredient.critical_stock_quantity.normalize(), "f"),
        status=ingredient.status,
        availableForNewUse=ingredient.available_for_new_use,
    )


def component_response(component: RecipeComponentView) -> RecipeComponentResponse:
    return RecipeComponentResponse(
        componentType=component.component_type,
        componentId=component.component_id,
        quantity=format(component.quantity.normalize(), "f"),
        unitId=component.unit_id,
    )


def cost_snapshot_response(snapshot: CostSnapshotView) -> CostSnapshotResponse:
    return CostSnapshotResponse(
        totalCost=format(snapshot.total_cost.normalize(), "f"),
        status=snapshot.status,
    )


def cost_projection_response(
    projection: CostProjectionView | None,
) -> CostProjectionResponse | None:
    if projection is None:
        return None
    return CostProjectionResponse(
        status=projection.status,
        updatedAt=projection.updated_at,
        lastError=projection.last_error,
    )


def sub_recipe_response(recipe: SubRecipeVersionView) -> SubRecipeVersionResponse:
    return SubRecipeVersionResponse(
        recipeId=recipe.recipe_id,
        recipeVersionId=recipe.recipe_version_id,
        name=recipe.name,
        code=recipe.code,
        version=recipe.version,
        yieldQuantity=format(recipe.yield_quantity.normalize(), "f"),
        yieldUnitId=recipe.yield_unit_id,
        effectiveFrom=recipe.effective_from,
        status=recipe.status,
        isActive=recipe.is_active,
        components=[component_response(component) for component in recipe.components],
        costSnapshot=cost_snapshot_response(recipe.cost_snapshot),
        costProjection=cost_projection_response(recipe.cost_projection),
    )


def branch_margin_response(margin: BranchMenuMarginView) -> BranchMenuMarginResponse:
    return BranchMenuMarginResponse(
        branchPriceId=margin.branch_price_id,
        menuItemVersionId=margin.menu_item_version_id,
        branchId=margin.branch_id,
        price=format(margin.price.normalize(), "f"),
        currency=margin.currency,
        theoreticalCost=format(margin.theoretical_cost.normalize(), "f"),
        contributionMargin=format(margin.contribution_margin.normalize(), "f"),
        marginPercent=format(margin.margin_percent.normalize(), "f"),
        suggestedPrice=format(margin.suggested_price.normalize(), "f"),
        effectiveFrom=margin.effective_from,
    )


def menu_item_response(recipe: MenuItemVersionView) -> MenuItemVersionResponse:
    return MenuItemVersionResponse(
        recipeId=recipe.recipe_id,
        recipeVersionId=recipe.recipe_version_id,
        name=recipe.name,
        code=recipe.code,
        version=recipe.version,
        yieldQuantity=format(recipe.yield_quantity.normalize(), "f"),
        yieldUnitId=recipe.yield_unit_id,
        effectiveFrom=recipe.effective_from,
        status=recipe.status,
        isActive=recipe.is_active,
        components=[component_response(component) for component in recipe.components],
        costSnapshot=cost_snapshot_response(recipe.cost_snapshot),
        branchMargins=[branch_margin_response(margin) for margin in recipe.branch_margins],
        costProjection=cost_projection_response(recipe.cost_projection),
    )


def create_menu_router(database_url: str | None = None) -> APIRouter:
    router = APIRouter(prefix="/api/v1/menu", tags=["menu-engineering"])
    resolved_database_url = database_url or os.environ.get("DATABASE_URL", "")
    platform_store = PostgresPlatformStore(resolved_database_url)
    menu_store = PostgresMenuCatalogStore(resolved_database_url)
    catalog = MenuCatalogService(store=menu_store)
    recipes = MenuRecipeService(store=menu_store)

    def menu_identity(gl_session: str | None) -> MenuIdentity:
        if not gl_session:
            raise AuthenticationRequired
        identity = platform_store.resolve_operating_identity(gl_session)
        return MenuIdentity(
            tenant_id=identity.tenant_id,
            actor_id=identity.actor_id,
            role=identity.role,
        )

    def menu_problem(error: Exception, correlation_id: str):
        if isinstance(error, AuthenticationRequired):
            return problem_response(401, "menu.authentication_required", correlation_id, [])
        if isinstance(error, MenuAuthorizationDenied):
            return problem_response(403, "menu.authorization_denied", correlation_id, [])
        if isinstance(error, MenuNotFound):
            return problem_response(404, "menu.catalog_not_found", correlation_id, [])
        if isinstance(error, MenuValidationError):
            return problem_response(
                422,
                "menu.catalog_invalid",
                correlation_id,
                [
                    {"field": detail.field, "code": detail.code, "detail": "review field"}
                    for detail in error.details
                ],
            )
        if isinstance(error, UnitDimensionMismatch):
            return problem_response(
                422,
                "menu.dimension_mismatch",
                correlation_id,
                [{"field": "dimension", "code": "mismatch", "detail": "review units"}],
            )
        if isinstance(error, UnitConversionUnavailable):
            return problem_response(
                409,
                "menu.conversion_unavailable",
                correlation_id,
                [{"field": "consumptionUnitId", "code": "missing_factor", "detail": "add factor"}],
            )
        if isinstance(error, (MenuCodeConflict, IngredientCodeConflict)):
            return problem_response(409, "menu.code_conflict", correlation_id, [])
        if isinstance(error, IngredientArchived):
            return problem_response(409, "menu.ingredient_archived", correlation_id, [])
        if isinstance(error, (RecipeCodeConflict, RecipeVersionConflict)):
            return problem_response(409, "menu.recipe_version_conflict", correlation_id, [])
        if isinstance(error, RecipeGraphViolation):
            return problem_response(409, "menu.recipe_graph_invalid", correlation_id, [])
        if isinstance(error, RecipeMissingCost):
            return problem_response(
                409,
                "menu.recipe_missing_cost",
                correlation_id,
                [{"field": "components", "code": "missing_cost", "detail": "add offer"}],
            )
        return problem_response(500, "menu.catalog_failed", correlation_id, [])

    @router.get(
        "/units",
        response_model=list[UnitResponse],
        operation_id="listMenuUnits",
        summary="List tenant units and conversion summaries",
        responses=MENU_RESPONSES,
    )
    def list_units(gl_session: str | None = Security(session_cookie)):
        correlation_id = str(uuid4())
        try:
            return [unit_response(unit) for unit in catalog.list_units(menu_identity(gl_session))]
        except (
            AuthenticationRequired,
            MenuAuthorizationDenied,
            psycopg.Error,
            SQLAlchemyError,
        ) as error:
            return menu_problem(error, correlation_id)

    @router.post(
        "/units",
        response_model=UnitResponse,
        status_code=201,
        operation_id="createMenuUnit",
        summary="Create a tenant unit",
        responses=MENU_RESPONSES,
    )
    def create_unit(request: UnitRequest, gl_session: str | None = Security(session_cookie)):
        correlation_id = str(uuid4())
        try:
            return unit_response(
                catalog.create_unit(
                    menu_identity(gl_session),
                    CreateUnit(
                        name=request.name,
                        code=request.code,
                        dimension=request.dimension,
                    ),
                    correlation_id=correlation_id,
                )
            )
        except (
            AuthenticationRequired,
            MenuAuthorizationDenied,
            MenuValidationError,
            MenuCodeConflict,
            psycopg.Error,
            SQLAlchemyError,
        ) as error:
            return menu_problem(error, correlation_id)

    @router.post(
        "/conversions",
        response_model=ConversionFactorResponse,
        status_code=201,
        operation_id="createMenuConversionFactor",
        summary="Create an effective-dated unit conversion factor",
        responses=MENU_RESPONSES,
    )
    def create_conversion_factor(
        request: ConversionFactorRequest,
        gl_session: str | None = Security(session_cookie),
    ):
        correlation_id = str(uuid4())
        try:
            return conversion_response(
                catalog.create_conversion_factor(
                    menu_identity(gl_session),
                    CreateConversionFactor(
                        source_unit_id=request.sourceUnitId,
                        target_unit_id=request.targetUnitId,
                        factor=request.factor,
                        effective_from=request.effectiveFrom,
                    ),
                    correlation_id=correlation_id,
                )
            )
        except (
            AuthenticationRequired,
            MenuAuthorizationDenied,
            MenuValidationError,
            MenuNotFound,
            MenuCodeConflict,
            UnitDimensionMismatch,
            psycopg.Error,
            SQLAlchemyError,
        ) as error:
            return menu_problem(error, correlation_id)

    @router.get(
        "/ingredients",
        response_model=list[IngredientResponse],
        operation_id="listMenuIngredients",
        summary="List tenant ingredients",
        responses=MENU_RESPONSES,
    )
    def list_ingredients(gl_session: str | None = Security(session_cookie)):
        correlation_id = str(uuid4())
        try:
            return [
                ingredient_response(ingredient)
                for ingredient in catalog.list_ingredients(menu_identity(gl_session))
            ]
        except (
            AuthenticationRequired,
            MenuAuthorizationDenied,
            psycopg.Error,
            SQLAlchemyError,
        ) as error:
            return menu_problem(error, correlation_id)

    @router.post(
        "/ingredients",
        response_model=IngredientResponse,
        status_code=201,
        operation_id="createMenuIngredient",
        summary="Create a tenant ingredient",
        responses=MENU_RESPONSES,
    )
    def create_ingredient(
        request: IngredientRequest,
        gl_session: str | None = Security(session_cookie),
    ):
        correlation_id = str(uuid4())
        try:
            return ingredient_response(
                catalog.create_ingredient(
                    menu_identity(gl_session),
                    CreateIngredient(
                        name=request.name,
                        code=request.code,
                        purchase_unit_id=request.purchaseUnitId,
                        consumption_unit_id=request.consumptionUnitId,
                        shelf_life_days=request.shelfLifeDays,
                        critical_stock_quantity=request.criticalStockQuantity,
                    ),
                    correlation_id=correlation_id,
                )
            )
        except (
            AuthenticationRequired,
            MenuAuthorizationDenied,
            MenuValidationError,
            MenuNotFound,
            IngredientCodeConflict,
            UnitConversionUnavailable,
            UnitDimensionMismatch,
            psycopg.Error,
            SQLAlchemyError,
        ) as error:
            return menu_problem(error, correlation_id)

    @router.post(
        "/ingredients/{ingredientId}/archive",
        response_model=IngredientResponse,
        operation_id="archiveMenuIngredient",
        summary="Archive a tenant ingredient",
        responses=MENU_RESPONSES,
    )
    def archive_ingredient(
        ingredientId: UUID,
        gl_session: str | None = Security(session_cookie),
    ):
        correlation_id = str(uuid4())
        try:
            return ingredient_response(
                catalog.archive_ingredient(
                    menu_identity(gl_session),
                    ArchiveIngredient(ingredient_id=str(ingredientId)),
                    correlation_id=correlation_id,
                )
            )
        except (
            AuthenticationRequired,
            MenuAuthorizationDenied,
            MenuNotFound,
            IngredientArchived,
            psycopg.Error,
            SQLAlchemyError,
        ) as error:
            return menu_problem(error, correlation_id)

    @router.get(
        "/recipes/sub-recipes",
        response_model=list[SubRecipeVersionResponse],
        operation_id="listSubRecipeVersions",
        summary="List tenant sub-recipe versions",
        responses=MENU_RESPONSES,
    )
    def list_sub_recipes(gl_session: str | None = Security(session_cookie)):
        correlation_id = str(uuid4())
        try:
            return [
                sub_recipe_response(recipe)
                for recipe in recipes.list_sub_recipes(menu_identity(gl_session))
            ]
        except (
            AuthenticationRequired,
            MenuAuthorizationDenied,
            psycopg.Error,
            SQLAlchemyError,
        ) as error:
            return menu_problem(error, correlation_id)

    @router.post(
        "/recipes/sub-recipes",
        response_model=SubRecipeVersionResponse,
        status_code=201,
        operation_id="approveSubRecipeVersion",
        summary="Approve an immutable sub-recipe version",
        responses=MENU_RESPONSES,
    )
    def approve_sub_recipe_version(
        request: SubRecipeVersionRequest,
        gl_session: str | None = Security(session_cookie),
    ):
        correlation_id = str(uuid4())
        try:
            return sub_recipe_response(
                recipes.approve_sub_recipe_version(
                    menu_identity(gl_session),
                    CreateSubRecipeVersion(
                        name=request.name,
                        code=request.code,
                        version=request.version,
                        yield_quantity=request.yieldQuantity,
                        yield_unit_id=request.yieldUnitId,
                        effective_from=request.effectiveFrom,
                        components=tuple(
                            CreateRecipeComponent(
                                component_type=component.componentType,
                                component_id=component.componentId,
                                quantity=component.quantity,
                                unit_id=component.unitId,
                            )
                            for component in request.components
                        ),
                    ),
                    correlation_id=correlation_id,
                )
            )
        except (
            AuthenticationRequired,
            MenuAuthorizationDenied,
            MenuValidationError,
            MenuNotFound,
            UnitConversionUnavailable,
            UnitDimensionMismatch,
            RecipeCodeConflict,
            RecipeVersionConflict,
            RecipeGraphViolation,
            RecipeMissingCost,
            psycopg.Error,
            SQLAlchemyError,
        ) as error:
            return menu_problem(error, correlation_id)

    @router.get(
        "/recipes/menu-items",
        response_model=list[MenuItemVersionResponse],
        operation_id="listMenuItemVersions",
        summary="List tenant menu item versions and branch margins",
        responses=MENU_RESPONSES,
    )
    def list_menu_items(gl_session: str | None = Security(session_cookie)):
        correlation_id = str(uuid4())
        try:
            return [
                menu_item_response(recipe)
                for recipe in recipes.list_menu_items(menu_identity(gl_session))
            ]
        except (
            AuthenticationRequired,
            MenuAuthorizationDenied,
            psycopg.Error,
            SQLAlchemyError,
        ) as error:
            return menu_problem(error, correlation_id)

    @router.post(
        "/recipes/menu-items",
        response_model=MenuItemVersionResponse,
        status_code=201,
        operation_id="approveMenuItemVersion",
        summary="Approve an immutable menu item version",
        responses=MENU_RESPONSES,
    )
    def approve_menu_item_version(
        request: MenuItemVersionRequest,
        gl_session: str | None = Security(session_cookie),
    ):
        correlation_id = str(uuid4())
        try:
            return menu_item_response(
                recipes.approve_menu_item_version(
                    menu_identity(gl_session),
                    CreateMenuItemVersion(
                        name=request.name,
                        code=request.code,
                        version=request.version,
                        yield_quantity=request.yieldQuantity,
                        yield_unit_id=request.yieldUnitId,
                        effective_from=request.effectiveFrom,
                        components=tuple(
                            CreateRecipeComponent(
                                component_type=component.componentType,
                                component_id=component.componentId,
                                quantity=component.quantity,
                                unit_id=component.unitId,
                            )
                            for component in request.components
                        ),
                    ),
                    correlation_id=correlation_id,
                )
            )
        except (
            AuthenticationRequired,
            MenuAuthorizationDenied,
            MenuValidationError,
            MenuNotFound,
            UnitConversionUnavailable,
            UnitDimensionMismatch,
            RecipeCodeConflict,
            RecipeVersionConflict,
            RecipeGraphViolation,
            RecipeMissingCost,
            psycopg.Error,
            SQLAlchemyError,
        ) as error:
            return menu_problem(error, correlation_id)

    @router.post(
        "/recipes/menu-items/{recipeVersionId}/branch-prices",
        response_model=BranchMenuMarginResponse,
        status_code=201,
        operation_id="createMenuItemBranchPrice",
        summary="Create an informational branch menu item price and margin",
        responses=MENU_RESPONSES,
    )
    def create_menu_item_branch_price(
        recipeVersionId: UUID,
        request: BranchMenuPriceRequest,
        gl_session: str | None = Security(session_cookie),
    ):
        correlation_id = str(uuid4())
        try:
            return branch_margin_response(
                recipes.create_branch_price(
                    menu_identity(gl_session),
                    CreateBranchMenuPrice(
                        menu_item_version_id=str(recipeVersionId),
                        branch_id=request.branchId,
                        price=request.price,
                        currency=request.currency,
                        effective_from=request.effectiveFrom,
                    ),
                    correlation_id=correlation_id,
                )
            )
        except (
            AuthenticationRequired,
            MenuAuthorizationDenied,
            MenuValidationError,
            MenuNotFound,
            RecipeVersionConflict,
            psycopg.Error,
            SQLAlchemyError,
        ) as error:
            return menu_problem(error, correlation_id)

    return router
