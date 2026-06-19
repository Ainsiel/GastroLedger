from datetime import UTC, date, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from psycopg import errors
from sqlalchemy import create_engine, desc, or_, select, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy.pool import NullPool

from gastroledger_api.modules.menu_engineering.application.catalog import (
    ConversionFactorView,
    IngredientArchived,
    IngredientCodeConflict,
    IngredientView,
    MenuAuthorizationDenied,
    MenuCodeConflict,
    MenuIdentity,
    MenuNotFound,
    UnitConversionResult,
    UnitConversionUnavailable,
    UnitDimensionMismatch,
    UnitView,
)
from gastroledger_api.modules.menu_engineering.application.recipes import (
    BranchMenuMarginView,
    CostSnapshotView,
    MenuItemVersionView,
    RecipeCodeConflict,
    RecipeComponentView,
    RecipeGraphViolation,
    RecipeMissingCost,
    RecipeVersionConflict,
    SubRecipeVersionView,
)
from gastroledger_api.modules.menu_engineering.domain.catalog import (
    ValidatedConversionFactor,
    ValidatedIngredient,
    ValidatedUnit,
)
from gastroledger_api.technical.menu_models import (
    MenuConversionFactor,
    MenuCostSnapshot,
    MenuIngredient,
    MenuItemBranchPrice,
    MenuRecipe,
    MenuRecipeComponent,
    MenuRecipeVersion,
    MenuUnit,
)
from gastroledger_api.technical.platform_models import (
    ControlAuditEvent,
    PlatformBranch,
    PlatformMembership,
)
from gastroledger_api.technical.postgres_platform import sqlalchemy_database_url
from gastroledger_api.technical.procurement_models import ProcurementSupplierOffer


class PostgresMenuCatalogStore:
    def __init__(self, database_url: str) -> None:
        self._database_url = database_url
        self._engine: Engine | None = None

    def _open_session(self) -> Session:
        if self._engine is None:
            self._engine = create_engine(
                sqlalchemy_database_url(self._database_url), poolclass=NullPool
            )
        return Session(self._engine)

    def list_units(self, identity: MenuIdentity) -> tuple[UnitView, ...]:
        with self._open_session() as session, session.begin():
            self._authorize_menu_identity(session, identity)
            units = session.execute(
                select(MenuUnit)
                .where(MenuUnit.tenant_id == UUID(identity.tenant_id))
                .order_by(MenuUnit.code)
            ).scalars()
            conversions = session.execute(
                select(MenuConversionFactor)
                .where(MenuConversionFactor.tenant_id == UUID(identity.tenant_id))
                .order_by(MenuConversionFactor.effective_from, MenuConversionFactor.id)
            ).scalars()
            by_source: dict[UUID, list[ConversionFactorView]] = {}
            for conversion in conversions:
                by_source.setdefault(conversion.source_unit_id, []).append(
                    self._conversion_view(conversion)
                )
            return tuple(
                UnitView(
                    unit_id=str(unit.id),
                    name=unit.name,
                    code=unit.code,
                    dimension=unit.dimension,
                    conversions=tuple(by_source.get(unit.id, [])),
                )
                for unit in units
            )

    def create_unit(
        self,
        identity: MenuIdentity,
        unit: ValidatedUnit,
        correlation_id: str,
    ) -> UnitView:
        unit_uuid = uuid4()
        try:
            with self._open_session() as session, session.begin():
                self._authorize_menu_identity(session, identity)
                record = MenuUnit(
                    id=unit_uuid,
                    tenant_id=UUID(identity.tenant_id),
                    code=unit.code,
                    name=unit.name,
                    dimension=unit.dimension,
                )
                session.add(record)
                session.flush()
                self._audit(
                    session,
                    identity,
                    correlation_id,
                    "menu.unit.created",
                    str(unit_uuid),
                )
                return UnitView(
                    unit_id=str(record.id),
                    name=record.name,
                    code=record.code,
                    dimension=record.dimension,
                )
        except IntegrityError as error:
            if isinstance(error.orig, errors.UniqueViolation):
                raise MenuCodeConflict from error
            raise

    def create_conversion_factor(
        self,
        identity: MenuIdentity,
        conversion: ValidatedConversionFactor,
        correlation_id: str,
    ) -> ConversionFactorView:
        conversion_uuid = uuid4()
        try:
            with self._open_session() as session, session.begin():
                self._authorize_menu_identity(session, identity)
                source, target = self._unit_pair(
                    session,
                    identity,
                    conversion.source_unit_id,
                    conversion.target_unit_id,
                )
                if source.dimension != target.dimension:
                    raise UnitDimensionMismatch
                record = MenuConversionFactor(
                    id=conversion_uuid,
                    tenant_id=UUID(identity.tenant_id),
                    source_unit_id=source.id,
                    target_unit_id=target.id,
                    factor=conversion.factor,
                    effective_from=conversion.effective_from,
                )
                session.add(record)
                session.flush()
                self._audit(
                    session,
                    identity,
                    correlation_id,
                    "menu.conversion_factor.created",
                    str(conversion_uuid),
                )
                return self._conversion_view(record)
        except IntegrityError as error:
            if isinstance(error.orig, errors.UniqueViolation):
                raise MenuCodeConflict from error
            raise

    def convert_quantity(
        self,
        identity: MenuIdentity,
        source_unit_id: str,
        target_unit_id: str,
        quantity: Decimal,
        as_of: date,
    ) -> UnitConversionResult:
        with self._open_session() as session, session.begin():
            self._authorize_menu_identity(session, identity)
            source, target = self._unit_pair(
                session,
                identity,
                source_unit_id,
                target_unit_id,
            )
            if source.id == target.id:
                return UnitConversionResult(quantity=quantity, target_unit_id=str(target.id))
            if source.dimension != target.dimension:
                raise UnitDimensionMismatch
            factor = self._current_factor(session, identity, source.id, target.id, as_of)
            return UnitConversionResult(
                quantity=quantity * factor,
                target_unit_id=str(target.id),
            )

    def list_ingredients(self, identity: MenuIdentity) -> tuple[IngredientView, ...]:
        with self._open_session() as session, session.begin():
            self._authorize_menu_identity(session, identity)
            ingredients = session.execute(
                select(MenuIngredient)
                .where(MenuIngredient.tenant_id == UUID(identity.tenant_id))
                .order_by(MenuIngredient.code)
            ).scalars()
            return tuple(self._ingredient_view(ingredient) for ingredient in ingredients)

    def create_ingredient(
        self,
        identity: MenuIdentity,
        ingredient: ValidatedIngredient,
        correlation_id: str,
    ) -> IngredientView:
        ingredient_uuid = uuid4()
        try:
            with self._open_session() as session, session.begin():
                self._authorize_menu_identity(session, identity)
                purchase, consumption = self._unit_pair(
                    session,
                    identity,
                    ingredient.purchase_unit_id,
                    ingredient.consumption_unit_id,
                )
                if purchase.dimension != consumption.dimension:
                    raise UnitDimensionMismatch
                if purchase.id != consumption.id:
                    self._current_factor(
                        session,
                        identity,
                        purchase.id,
                        consumption.id,
                        date.today(),
                    )
                record = MenuIngredient(
                    id=ingredient_uuid,
                    tenant_id=UUID(identity.tenant_id),
                    code=ingredient.code,
                    name=ingredient.name,
                    purchase_unit_id=purchase.id,
                    consumption_unit_id=consumption.id,
                    shelf_life_days=ingredient.shelf_life_days,
                    critical_stock_quantity=ingredient.critical_stock_quantity,
                    status="active",
                )
                session.add(record)
                session.flush()
                self._audit(
                    session,
                    identity,
                    correlation_id,
                    "menu.ingredient.created",
                    str(ingredient_uuid),
                )
                return self._ingredient_view(record)
        except IntegrityError as error:
            if isinstance(error.orig, errors.UniqueViolation):
                raise IngredientCodeConflict from error
            raise

    def archive_ingredient(
        self,
        identity: MenuIdentity,
        ingredient_id: str,
        correlation_id: str,
    ) -> IngredientView:
        with self._open_session() as session, session.begin():
            self._authorize_menu_identity(session, identity)
            ingredient = session.execute(
                select(MenuIngredient)
                .where(
                    MenuIngredient.id == UUID(ingredient_id),
                    MenuIngredient.tenant_id == UUID(identity.tenant_id),
                )
                .with_for_update()
            ).scalar_one_or_none()
            if ingredient is None:
                raise MenuNotFound
            if ingredient.status == "archived":
                raise IngredientArchived
            ingredient.status = "archived"
            self._audit(
                session,
                identity,
                correlation_id,
                "menu.ingredient.archived",
                str(ingredient.id),
            )
            return self._ingredient_view(ingredient)

    def list_sub_recipes(self, identity: MenuIdentity) -> tuple[SubRecipeVersionView, ...]:
        with self._open_session() as session, session.begin():
            self._authorize_menu_identity(session, identity)
            versions = session.execute(
                select(MenuRecipeVersion)
                .join(MenuRecipe, MenuRecipeVersion.recipe_id == MenuRecipe.id)
                .where(
                    MenuRecipeVersion.tenant_id == UUID(identity.tenant_id),
                    MenuRecipe.recipe_type == "sub_recipe",
                )
                .order_by(MenuRecipe.code, MenuRecipeVersion.effective_from)
            ).scalars()
            return tuple(self._sub_recipe_view(session, version) for version in versions)

    def list_menu_items(self, identity: MenuIdentity) -> tuple[MenuItemVersionView, ...]:
        with self._open_session() as session, session.begin():
            self._authorize_menu_identity(session, identity)
            versions = session.execute(
                select(MenuRecipeVersion)
                .join(MenuRecipe, MenuRecipeVersion.recipe_id == MenuRecipe.id)
                .where(
                    MenuRecipeVersion.tenant_id == UUID(identity.tenant_id),
                    MenuRecipe.recipe_type == "menu_item",
                )
                .order_by(MenuRecipe.code, MenuRecipeVersion.effective_from)
            ).scalars()
            return tuple(self._menu_item_view(session, version) for version in versions)

    def approve_sub_recipe_version(
        self,
        identity: MenuIdentity,
        recipe: object,
        correlation_id: str,
    ) -> SubRecipeVersionView:
        recipe_uuid = uuid4()
        version_uuid = uuid4()
        try:
            with self._open_session() as session, session.begin():
                self._authorize_menu_identity(session, identity)
                tenant_uuid = UUID(identity.tenant_id)
                yield_unit = self._unit(session, identity, recipe.yield_unit_id)
                record = session.execute(
                    select(MenuRecipe)
                    .where(MenuRecipe.tenant_id == tenant_uuid, MenuRecipe.code == recipe.code)
                ).scalar_one_or_none()
                if record is None:
                    record = MenuRecipe(
                        id=recipe_uuid,
                        tenant_id=tenant_uuid,
                        code=recipe.code,
                        name=recipe.name,
                        recipe_type="sub_recipe",
                    )
                    session.add(record)
                    session.flush()
                elif record.recipe_type != "sub_recipe":
                    raise RecipeCodeConflict

                self._ensure_recipe_graph_allowed(session, identity, record.id, recipe)
                status = "scheduled" if recipe.effective_from > date.today() else "approved"
                version = MenuRecipeVersion(
                    id=version_uuid,
                    tenant_id=tenant_uuid,
                    recipe_id=record.id,
                    version=recipe.version,
                    yield_quantity=recipe.yield_quantity,
                    yield_unit_id=yield_unit.id,
                    effective_from=recipe.effective_from,
                    status=status,
                    approved_at=datetime.now(UTC),
                )
                session.add(version)
                total_cost = self._record_recipe_components(
                    session,
                    identity,
                    version,
                    recipe,
                    yield_unit,
                    allow_sub_recipes=False,
                )
                session.add(
                    MenuCostSnapshot(
                        id=uuid4(),
                        tenant_id=tenant_uuid,
                        recipe_version_id=version.id,
                        as_of=recipe.effective_from,
                        total_cost=total_cost,
                        status="current",
                    )
                )
                session.flush()
                self._audit(
                    session,
                    identity,
                    correlation_id,
                    "menu.sub_recipe_version.approved",
                    str(version.id),
                )
                return self._sub_recipe_view(session, version)
        except IntegrityError as error:
            if isinstance(error.orig, errors.UniqueViolation):
                raise RecipeVersionConflict from error
            raise

    def approve_menu_item_version(
        self,
        identity: MenuIdentity,
        recipe: object,
        correlation_id: str,
    ) -> MenuItemVersionView:
        recipe_uuid = uuid4()
        version_uuid = uuid4()
        try:
            with self._open_session() as session, session.begin():
                self._authorize_menu_identity(session, identity)
                tenant_uuid = UUID(identity.tenant_id)
                yield_unit = self._unit(session, identity, recipe.yield_unit_id)
                record = session.execute(
                    select(MenuRecipe)
                    .where(MenuRecipe.tenant_id == tenant_uuid, MenuRecipe.code == recipe.code)
                ).scalar_one_or_none()
                if record is None:
                    record = MenuRecipe(
                        id=recipe_uuid,
                        tenant_id=tenant_uuid,
                        code=recipe.code,
                        name=recipe.name,
                        recipe_type="menu_item",
                    )
                    session.add(record)
                    session.flush()
                elif record.recipe_type != "menu_item":
                    raise RecipeCodeConflict

                status = "scheduled" if recipe.effective_from > date.today() else "approved"
                version = MenuRecipeVersion(
                    id=version_uuid,
                    tenant_id=tenant_uuid,
                    recipe_id=record.id,
                    version=recipe.version,
                    yield_quantity=recipe.yield_quantity,
                    yield_unit_id=yield_unit.id,
                    effective_from=recipe.effective_from,
                    status=status,
                    approved_at=datetime.now(UTC),
                )
                session.add(version)
                total_cost = self._record_recipe_components(
                    session,
                    identity,
                    version,
                    recipe,
                    yield_unit,
                    allow_sub_recipes=True,
                )
                session.add(
                    MenuCostSnapshot(
                        id=uuid4(),
                        tenant_id=tenant_uuid,
                        recipe_version_id=version.id,
                        as_of=recipe.effective_from,
                        total_cost=total_cost,
                        status="current",
                    )
                )
                session.flush()
                self._audit(
                    session,
                    identity,
                    correlation_id,
                    "menu.menu_item_version.approved",
                    str(version.id),
                )
                return self._menu_item_view(session, version)
        except IntegrityError as error:
            if isinstance(error.orig, errors.UniqueViolation):
                raise RecipeVersionConflict from error
            raise

    def create_branch_price(
        self,
        identity: MenuIdentity,
        price: object,
        correlation_id: str,
    ) -> BranchMenuMarginView:
        price_uuid = uuid4()
        try:
            with self._open_session() as session, session.begin():
                self._authorize_menu_identity(session, identity)
                tenant_uuid = UUID(identity.tenant_id)
                version = self._menu_item_version(session, identity, price.menu_item_version_id)
                self._branch(session, identity, price.branch_id)
                record = MenuItemBranchPrice(
                    id=price_uuid,
                    tenant_id=tenant_uuid,
                    recipe_version_id=version.id,
                    branch_id=UUID(price.branch_id),
                    price=price.price,
                    currency=price.currency,
                    effective_from=price.effective_from,
                )
                session.add(record)
                session.flush()
                self._audit(
                    session,
                    identity,
                    correlation_id,
                    "menu.menu_item_branch_price.created",
                    str(record.id),
                )
                return self._branch_margin_view(session, record)
        except IntegrityError as error:
            if isinstance(error.orig, errors.UniqueViolation):
                raise RecipeVersionConflict from error
            raise

    @staticmethod
    def _authorize_menu_identity(session: Session, identity: MenuIdentity) -> None:
        session.execute(text("set local role gastroledger_app"))
        session.execute(
            text("select set_config('app.current_tenant_id', :tenant_id, true)"),
            {"tenant_id": str(identity.tenant_id)},
        )
        role = session.execute(
            select(PlatformMembership.role).where(
                PlatformMembership.tenant_id == UUID(identity.tenant_id),
                PlatformMembership.user_id == UUID(identity.actor_id),
            )
        ).scalar_one_or_none()
        if role not in {"menu_engineer", "tenant_admin"}:
            raise MenuAuthorizationDenied

    @staticmethod
    def _audit(
        session: Session,
        identity: MenuIdentity,
        correlation_id: str,
        action: str,
        object_reference: str,
    ) -> None:
        session.add(
            ControlAuditEvent(
                id=uuid4(),
                tenant_id=UUID(identity.tenant_id),
                actor_id=UUID(identity.actor_id),
                correlation_id=correlation_id,
                action=action,
                object_reference=object_reference,
                occurred_at=datetime.now(UTC),
            )
        )

    @staticmethod
    def _conversion_view(conversion: MenuConversionFactor) -> ConversionFactorView:
        return ConversionFactorView(
            conversion_factor_id=str(conversion.id),
            source_unit_id=str(conversion.source_unit_id),
            target_unit_id=str(conversion.target_unit_id),
            factor=conversion.factor,
            effective_from=conversion.effective_from,
        )

    @staticmethod
    def _ingredient_view(ingredient: MenuIngredient) -> IngredientView:
        return IngredientView(
            ingredient_id=str(ingredient.id),
            name=ingredient.name,
            code=ingredient.code,
            purchase_unit_id=str(ingredient.purchase_unit_id),
            consumption_unit_id=str(ingredient.consumption_unit_id),
            shelf_life_days=ingredient.shelf_life_days,
            critical_stock_quantity=ingredient.critical_stock_quantity,
            status=ingredient.status,
            available_for_new_use=ingredient.status == "active",
        )

    @staticmethod
    def _unit_pair(
        session: Session,
        identity: MenuIdentity,
        source_unit_id: str,
        target_unit_id: str,
    ) -> tuple[MenuUnit, MenuUnit]:
        units = session.execute(
            select(MenuUnit).where(
                MenuUnit.tenant_id == UUID(identity.tenant_id),
                MenuUnit.id.in_([UUID(source_unit_id), UUID(target_unit_id)]),
            )
        ).scalars()
        by_id = {unit.id: unit for unit in units}
        try:
            return by_id[UUID(source_unit_id)], by_id[UUID(target_unit_id)]
        except KeyError as error:
            raise MenuNotFound from error

    @staticmethod
    def _unit(session: Session, identity: MenuIdentity, unit_id: str) -> MenuUnit:
        unit = session.execute(
            select(MenuUnit).where(
                MenuUnit.tenant_id == UUID(identity.tenant_id),
                MenuUnit.id == UUID(unit_id),
            )
        ).scalar_one_or_none()
        if unit is None:
            raise MenuNotFound
        return unit

    @staticmethod
    def _active_ingredient(
        session: Session,
        identity: MenuIdentity,
        ingredient_id: str,
    ) -> MenuIngredient:
        ingredient = session.execute(
            select(MenuIngredient).where(
                MenuIngredient.tenant_id == UUID(identity.tenant_id),
                MenuIngredient.id == UUID(ingredient_id),
                MenuIngredient.status == "active",
            )
        ).scalar_one_or_none()
        if ingredient is None:
            raise MenuNotFound
        return ingredient

    @staticmethod
    def _branch(session: Session, identity: MenuIdentity, branch_id: str) -> PlatformBranch:
        branch = session.execute(
            select(PlatformBranch).where(
                PlatformBranch.tenant_id == UUID(identity.tenant_id),
                PlatformBranch.id == UUID(branch_id),
            )
        ).scalar_one_or_none()
        if branch is None:
            raise MenuNotFound
        return branch

    @staticmethod
    def _menu_item_version(
        session: Session,
        identity: MenuIdentity,
        recipe_version_id: str,
    ) -> MenuRecipeVersion:
        version = session.execute(
            select(MenuRecipeVersion)
            .join(MenuRecipe, MenuRecipeVersion.recipe_id == MenuRecipe.id)
            .where(
                MenuRecipeVersion.tenant_id == UUID(identity.tenant_id),
                MenuRecipeVersion.id == UUID(recipe_version_id),
                MenuRecipe.recipe_type == "menu_item",
            )
        ).scalar_one_or_none()
        if version is None:
            raise MenuNotFound
        return version

    def _record_recipe_components(
        self,
        session: Session,
        identity: MenuIdentity,
        version: MenuRecipeVersion,
        recipe: object,
        yield_unit: MenuUnit,
        *,
        allow_sub_recipes: bool,
    ) -> Decimal:
        tenant_uuid = UUID(identity.tenant_id)
        total_cost = Decimal("0")
        for component in recipe.components:
            unit = self._unit(session, identity, component.unit_id)
            if unit.dimension != yield_unit.dimension:
                raise UnitDimensionMismatch
            if component.component_type == "sub_recipe":
                if not allow_sub_recipes:
                    raise RecipeGraphViolation("sub_recipe_depth")
                component_recipe = self._active_sub_recipe(
                    session,
                    identity,
                    component.component_id,
                    component.unit_id,
                    recipe.effective_from,
                )
                total_cost += (
                    component.quantity
                    / component_recipe.yield_quantity
                    * self._cost_snapshot(session, component_recipe.id).total_cost
                )
                session.add(
                    MenuRecipeComponent(
                        id=uuid4(),
                        tenant_id=tenant_uuid,
                        recipe_version_id=version.id,
                        component_type="sub_recipe",
                        ingredient_id=None,
                        component_recipe_id=UUID(component.component_id),
                        quantity=component.quantity,
                        unit_id=unit.id,
                    )
                )
                continue

            ingredient = self._active_ingredient(
                session,
                identity,
                component.component_id,
            )
            if ingredient.consumption_unit_id != unit.id:
                raise UnitConversionUnavailable
            offer_price = self._current_offer_price(
                session,
                identity,
                ingredient.id,
                unit.id,
                recipe.effective_from,
            )
            total_cost += component.quantity * offer_price
            session.add(
                MenuRecipeComponent(
                    id=uuid4(),
                    tenant_id=tenant_uuid,
                    recipe_version_id=version.id,
                    component_type="ingredient",
                    ingredient_id=ingredient.id,
                    component_recipe_id=None,
                    quantity=component.quantity,
                    unit_id=unit.id,
                )
            )
        return total_cost

    @staticmethod
    def _active_sub_recipe(
        session: Session,
        identity: MenuIdentity,
        recipe_id: str,
        unit_id: str,
        as_of: date,
    ) -> MenuRecipeVersion:
        version = session.execute(
            select(MenuRecipeVersion)
            .join(MenuRecipe, MenuRecipeVersion.recipe_id == MenuRecipe.id)
            .where(
                MenuRecipe.tenant_id == UUID(identity.tenant_id),
                MenuRecipe.id == UUID(recipe_id),
                MenuRecipe.recipe_type == "sub_recipe",
                MenuRecipeVersion.status == "approved",
                MenuRecipeVersion.effective_from <= as_of,
                MenuRecipeVersion.yield_unit_id == UUID(unit_id),
            )
            .order_by(desc(MenuRecipeVersion.effective_from))
            .limit(1)
        ).scalar_one_or_none()
        if version is None:
            raise RecipeMissingCost
        return version

    @staticmethod
    def _cost_snapshot(session: Session, recipe_version_id: UUID) -> MenuCostSnapshot:
        snapshot = session.execute(
            select(MenuCostSnapshot).where(MenuCostSnapshot.recipe_version_id == recipe_version_id)
        ).scalar_one_or_none()
        if snapshot is None or snapshot.status != "current":
            raise RecipeMissingCost
        return snapshot

    @staticmethod
    def _ensure_recipe_graph_allowed(
        session: Session,
        identity: MenuIdentity,
        recipe_id: UUID,
        recipe: object,
    ) -> None:
        for component in recipe.components:
            if component.component_type != "sub_recipe":
                continue
            component_recipe_id = UUID(component.component_id)
            if component_recipe_id == recipe_id:
                raise RecipeGraphViolation("cycle")
            exists = session.execute(
                select(MenuRecipe.id).where(
                    MenuRecipe.tenant_id == UUID(identity.tenant_id),
                    MenuRecipe.id == component_recipe_id,
                    MenuRecipe.recipe_type == "sub_recipe",
                )
            ).scalar_one_or_none()
            if exists is None:
                raise MenuNotFound
            raise RecipeGraphViolation("sub_recipe_depth")

    @staticmethod
    def _current_offer_price(
        session: Session,
        identity: MenuIdentity,
        ingredient_id: UUID,
        unit_id: UUID,
        as_of: date,
    ) -> Decimal:
        price = session.execute(
            select(ProcurementSupplierOffer.price)
            .where(
                ProcurementSupplierOffer.tenant_id == UUID(identity.tenant_id),
                ProcurementSupplierOffer.ingredient_id == ingredient_id,
                ProcurementSupplierOffer.purchase_unit_id == unit_id,
                ProcurementSupplierOffer.effective_from <= as_of,
                or_(
                    ProcurementSupplierOffer.effective_until.is_(None),
                    ProcurementSupplierOffer.effective_until >= as_of,
                ),
            )
            .order_by(ProcurementSupplierOffer.price, desc(ProcurementSupplierOffer.effective_from))
            .limit(1)
        ).scalar_one_or_none()
        if price is None:
            raise RecipeMissingCost
        return price

    @staticmethod
    def _sub_recipe_view(
        session: Session,
        version: MenuRecipeVersion,
    ) -> SubRecipeVersionView:
        recipe = session.execute(
            select(MenuRecipe).where(MenuRecipe.id == version.recipe_id)
        ).scalar_one()
        components = session.execute(
            select(MenuRecipeComponent)
            .where(MenuRecipeComponent.recipe_version_id == version.id)
            .order_by(MenuRecipeComponent.id)
        ).scalars()
        snapshot = session.execute(
            select(MenuCostSnapshot).where(MenuCostSnapshot.recipe_version_id == version.id)
        ).scalar_one()
        return SubRecipeVersionView(
            recipe_id=str(recipe.id),
            recipe_version_id=str(version.id),
            name=recipe.name,
            code=recipe.code,
            version=version.version,
            yield_quantity=version.yield_quantity,
            yield_unit_id=str(version.yield_unit_id),
            effective_from=version.effective_from,
            status=version.status,
            is_active=version.status == "approved" and version.effective_from <= date.today(),
            components=tuple(
                RecipeComponentView(
                    component_type=component.component_type,
                    component_id=str(
                        component.ingredient_id or component.component_recipe_id
                    ),
                    quantity=component.quantity,
                    unit_id=str(component.unit_id),
                )
                for component in components
            ),
            cost_snapshot=CostSnapshotView(
                total_cost=snapshot.total_cost,
                status=snapshot.status,
            ),
        )

    @staticmethod
    def _menu_item_view(
        session: Session,
        version: MenuRecipeVersion,
    ) -> MenuItemVersionView:
        recipe = session.execute(
            select(MenuRecipe).where(MenuRecipe.id == version.recipe_id)
        ).scalar_one()
        components = session.execute(
            select(MenuRecipeComponent)
            .where(MenuRecipeComponent.recipe_version_id == version.id)
            .order_by(MenuRecipeComponent.id)
        ).scalars()
        snapshot = session.execute(
            select(MenuCostSnapshot).where(MenuCostSnapshot.recipe_version_id == version.id)
        ).scalar_one()
        branch_prices = session.execute(
            select(MenuItemBranchPrice)
            .where(MenuItemBranchPrice.recipe_version_id == version.id)
            .order_by(MenuItemBranchPrice.effective_from, MenuItemBranchPrice.branch_id)
        ).scalars()
        return MenuItemVersionView(
            recipe_id=str(recipe.id),
            recipe_version_id=str(version.id),
            name=recipe.name,
            code=recipe.code,
            version=version.version,
            yield_quantity=version.yield_quantity,
            yield_unit_id=str(version.yield_unit_id),
            effective_from=version.effective_from,
            status=version.status,
            is_active=version.status == "approved" and version.effective_from <= date.today(),
            components=tuple(
                RecipeComponentView(
                    component_type=component.component_type,
                    component_id=str(component.ingredient_id or component.component_recipe_id),
                    quantity=component.quantity,
                    unit_id=str(component.unit_id),
                )
                for component in components
            ),
            cost_snapshot=CostSnapshotView(
                total_cost=snapshot.total_cost,
                status=snapshot.status,
            ),
            branch_margins=tuple(
                PostgresMenuCatalogStore._branch_margin_view(session, branch_price)
                for branch_price in branch_prices
            ),
        )

    @staticmethod
    def _branch_margin_view(
        session: Session,
        branch_price: MenuItemBranchPrice,
    ) -> BranchMenuMarginView:
        snapshot = session.execute(
            select(MenuCostSnapshot).where(
                MenuCostSnapshot.recipe_version_id == branch_price.recipe_version_id
            )
        ).scalar_one()
        contribution_margin = branch_price.price - snapshot.total_cost
        margin_percent = (
            contribution_margin / branch_price.price * Decimal("100")
            if branch_price.price > 0
            else Decimal("0")
        )
        return BranchMenuMarginView(
            branch_price_id=str(branch_price.id),
            menu_item_version_id=str(branch_price.recipe_version_id),
            branch_id=str(branch_price.branch_id),
            price=branch_price.price,
            currency=branch_price.currency,
            theoretical_cost=snapshot.total_cost,
            contribution_margin=contribution_margin,
            margin_percent=margin_percent,
            suggested_price=snapshot.total_cost * Decimal("3"),
            effective_from=branch_price.effective_from,
        )

    @staticmethod
    def _current_factor(
        session: Session,
        identity: MenuIdentity,
        source_unit_id: UUID,
        target_unit_id: UUID,
        as_of: date,
    ) -> Decimal:
        factor = session.execute(
            select(MenuConversionFactor.factor)
            .where(
                MenuConversionFactor.tenant_id == UUID(identity.tenant_id),
                MenuConversionFactor.source_unit_id == source_unit_id,
                MenuConversionFactor.target_unit_id == target_unit_id,
                MenuConversionFactor.effective_from <= as_of,
            )
            .order_by(desc(MenuConversionFactor.effective_from))
            .limit(1)
        ).scalar_one_or_none()
        if factor is None:
            raise UnitConversionUnavailable
        return factor
