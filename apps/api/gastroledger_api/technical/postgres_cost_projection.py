from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import create_engine, desc, or_, select, text
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import NullPool

from gastroledger_api.technical.cost_projection_models import (
    MenuCostProjectionSnapshot,
    MenuCostProjectionState,
)
from gastroledger_api.technical.menu_models import (
    MenuCostSnapshot,
    MenuRecipe,
    MenuRecipeComponent,
    MenuRecipeVersion,
)
from gastroledger_api.technical.postgres_platform import sqlalchemy_database_url
from gastroledger_api.technical.procurement_models import ProcurementSupplierOffer


@dataclass(frozen=True)
class CostRecalculationJob:
    job_id: str
    tenant_id: str
    correlation_id: str
    ingredient_id: str


class PostgresCostRecalculationStore:
    def __init__(self, database_url: str) -> None:
        self._database_url = database_url
        self._engine: Engine | None = None

    def _open_session(self) -> Session:
        if self._engine is None:
            self._engine = create_engine(
                sqlalchemy_database_url(self._database_url), poolclass=NullPool
            )
        return Session(self._engine)

    def lease_next(self, worker_id: str) -> CostRecalculationJob | None:
        with self._open_session() as session, session.begin():
            session.execute(text("set local role gastroledger_app"))
            row = session.execute(
                text("select * from lease_cost_recalculation_job(:worker_id, 60)"),
                {"worker_id": worker_id},
            ).mappings().one_or_none()
            if row is None:
                return None
            return CostRecalculationJob(
                job_id=str(row["job_id"]),
                tenant_id=str(row["tenant_id"]),
                correlation_id=row["correlation_id"],
                ingredient_id=row["ingredient_id"],
            )

    def recalculate(self, job: CostRecalculationJob) -> None:
        tenant_id = UUID(job.tenant_id)
        ingredient_id = UUID(job.ingredient_id)
        with self._open_session() as session, session.begin():
            self._set_tenant(session, tenant_id)
            direct_versions = tuple(
                session.execute(
                    select(MenuRecipeVersion)
                    .join(
                        MenuRecipeComponent,
                        MenuRecipeComponent.recipe_version_id == MenuRecipeVersion.id,
                    )
                    .join(MenuRecipe, MenuRecipeVersion.recipe_id == MenuRecipe.id)
                    .where(
                        MenuRecipeVersion.tenant_id == tenant_id,
                        MenuRecipeVersion.status == "approved",
                        MenuRecipeVersion.effective_from <= date.today(),
                        MenuRecipeComponent.ingredient_id == ingredient_id,
                    )
                ).scalars()
            )
            direct_recipe_ids: set[UUID] = set()
            menu_versions: dict[UUID, MenuRecipeVersion] = {}
            for version in direct_versions:
                recipe_type = session.execute(
                    select(MenuRecipe.recipe_type).where(MenuRecipe.id == version.recipe_id)
                ).scalar_one()
                if recipe_type == "sub_recipe":
                    self._project_version(session, job, version)
                    direct_recipe_ids.add(version.recipe_id)
                else:
                    menu_versions[version.id] = version

            if direct_recipe_ids:
                dependent_menu_versions = session.execute(
                    select(MenuRecipeVersion)
                    .join(
                        MenuRecipeComponent,
                        MenuRecipeComponent.recipe_version_id == MenuRecipeVersion.id,
                    )
                    .join(MenuRecipe, MenuRecipeVersion.recipe_id == MenuRecipe.id)
                    .where(
                        MenuRecipeVersion.tenant_id == tenant_id,
                        MenuRecipeVersion.status == "approved",
                        MenuRecipeVersion.effective_from <= date.today(),
                        MenuRecipe.recipe_type == "menu_item",
                        MenuRecipeComponent.component_recipe_id.in_(direct_recipe_ids),
                    )
                ).scalars()
                menu_versions.update(
                    (version.id, version) for version in dependent_menu_versions
                )
            for version in menu_versions.values():
                self._project_version(session, job, version)

    def complete(self, job: CostRecalculationJob) -> None:
        now = datetime.now(UTC)
        with self._open_session() as session, session.begin():
            self._set_tenant(session, UUID(job.tenant_id))
            session.execute(
                text(
                    """
                    update control_jobs
                    set status = 'completed', lease_until = null, leased_by = null,
                        last_error = null, updated_at = :now
                    where id = :job_id and tenant_id = :tenant_id
                    """
                ),
                {"job_id": job.job_id, "tenant_id": job.tenant_id, "now": now},
            )
            session.execute(
                text(
                    """
                    update control_outbox_events
                    set status = 'processed', processed_at = :now, last_error = null
                    where tenant_id = :tenant_id and status = 'pending'
                      and payload ->> 'ingredientId' = :ingredient_id
                    """
                ),
                {"tenant_id": job.tenant_id, "ingredient_id": job.ingredient_id, "now": now},
            )

    def fail(self, job: CostRecalculationJob, detail: str) -> None:
        now = datetime.now(UTC)
        with self._open_session() as session, session.begin():
            self._set_tenant(session, UUID(job.tenant_id))
            session.execute(
                text(
                    """
                    update control_jobs
                    set status = case when attempts >= 3 then 'failed' else 'queued' end,
                        available_at = :retry_at, lease_until = null, leased_by = null,
                        last_error = :detail, updated_at = :now
                    where id = :job_id and tenant_id = :tenant_id
                    """
                ),
                {
                    "job_id": job.job_id,
                    "tenant_id": job.tenant_id,
                    "detail": detail[:500],
                    "now": now,
                    "retry_at": now + timedelta(seconds=30),
                },
            )
            session.execute(
                text(
                    """
                    update control_outbox_events
                    set attempts = attempts + 1, last_error = :detail
                    where tenant_id = :tenant_id and status = 'pending'
                      and event_type = 'procurement.supplier_offer.accepted'
                    """
                ),
                {
                    "tenant_id": job.tenant_id,
                    "detail": detail[:500],
                },
            )
            try:
                ingredient_id = UUID(job.ingredient_id)
            except ValueError:
                return
            affected = session.execute(
                select(MenuRecipeVersion.id)
                .join(
                    MenuRecipeComponent,
                    MenuRecipeComponent.recipe_version_id == MenuRecipeVersion.id,
                )
                .where(
                    MenuRecipeVersion.tenant_id == UUID(job.tenant_id),
                    MenuRecipeComponent.ingredient_id == ingredient_id,
                )
            ).scalars()
            for version_id in set(affected):
                self._set_projection_state(
                    session, UUID(job.tenant_id), version_id, "failed", now, detail[:500]
                )

    def _project_version(
        self,
        session: Session,
        job: CostRecalculationJob,
        version: MenuRecipeVersion,
    ) -> None:
        total_cost = Decimal("0")
        components = session.execute(
            select(MenuRecipeComponent).where(
                MenuRecipeComponent.recipe_version_id == version.id
            )
        ).scalars()
        for component in components:
            if component.ingredient_id is not None:
                total_cost += component.quantity * self._offer_price(
                    session, version.tenant_id, component.ingredient_id, component.unit_id
                )
                continue
            sub_version = session.execute(
                select(MenuRecipeVersion)
                .where(
                    MenuRecipeVersion.tenant_id == version.tenant_id,
                    MenuRecipeVersion.recipe_id == component.component_recipe_id,
                    MenuRecipeVersion.status == "approved",
                    MenuRecipeVersion.effective_from <= date.today(),
                )
                .order_by(desc(MenuRecipeVersion.effective_from))
                .limit(1)
            ).scalar_one()
            total_cost += (
                component.quantity
                / sub_version.yield_quantity
                * self._latest_cost(session, sub_version.id)
            )
        now = datetime.now(UTC)
        statement = insert(MenuCostProjectionSnapshot).values(
            id=uuid4(),
            tenant_id=version.tenant_id,
            recipe_version_id=version.id,
            source_job_id=UUID(job.job_id),
            total_cost=total_cost,
            calculated_at=now,
        )
        session.execute(
            statement.on_conflict_do_nothing(
                index_elements=[
                    MenuCostProjectionSnapshot.tenant_id,
                    MenuCostProjectionSnapshot.recipe_version_id,
                    MenuCostProjectionSnapshot.source_job_id,
                ]
            )
        )
        self._set_projection_state(session, version.tenant_id, version.id, "current", now, None)

    @staticmethod
    def _offer_price(
        session: Session, tenant_id: UUID, ingredient_id: UUID, unit_id: UUID
    ) -> Decimal:
        price = session.execute(
            select(ProcurementSupplierOffer.price)
            .where(
                ProcurementSupplierOffer.tenant_id == tenant_id,
                ProcurementSupplierOffer.ingredient_id == ingredient_id,
                ProcurementSupplierOffer.purchase_unit_id == unit_id,
                ProcurementSupplierOffer.effective_from <= date.today(),
                or_(
                    ProcurementSupplierOffer.effective_until.is_(None),
                    ProcurementSupplierOffer.effective_until >= date.today(),
                ),
            )
            .order_by(ProcurementSupplierOffer.price)
            .limit(1)
        ).scalar_one_or_none()
        if price is None:
            raise RuntimeError("missing_cost")
        return price

    @staticmethod
    def _latest_cost(session: Session, recipe_version_id: UUID) -> Decimal:
        projected = session.execute(
            select(MenuCostProjectionSnapshot.total_cost)
            .where(MenuCostProjectionSnapshot.recipe_version_id == recipe_version_id)
            .order_by(desc(MenuCostProjectionSnapshot.calculated_at))
            .limit(1)
        ).scalar_one_or_none()
        if projected is not None:
            return projected
        return session.execute(
            select(MenuCostSnapshot.total_cost).where(
                MenuCostSnapshot.recipe_version_id == recipe_version_id
            )
        ).scalar_one()

    @staticmethod
    def _set_projection_state(
        session: Session,
        tenant_id: UUID,
        recipe_version_id: UUID,
        status: str,
        updated_at: datetime,
        last_error: str | None,
    ) -> None:
        statement = insert(MenuCostProjectionState).values(
            recipe_version_id=recipe_version_id,
            tenant_id=tenant_id,
            status=status,
            updated_at=updated_at,
            last_error=last_error,
        )
        session.execute(
            statement.on_conflict_do_update(
                index_elements=[MenuCostProjectionState.recipe_version_id],
                set_={"status": status, "updated_at": updated_at, "last_error": last_error},
            )
        )

    @staticmethod
    def _set_tenant(session: Session, tenant_id: UUID) -> None:
        session.execute(text("set local role gastroledger_app"))
        session.execute(
            text("select set_config('app.current_tenant_id', :tenant_id, true)"),
            {"tenant_id": str(tenant_id)},
        )
