from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from uuid import UUID, uuid4

from sqlalchemy import create_engine, select, text
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import NullPool

from gastroledger_api.modules.inventory_production.application.expiry_alerts import (
    ExpiryAlertConflict,
    ExpiryAlertIdentity,
    ExpiryAlertNotFound,
    ExpiryAlertView,
)
from gastroledger_api.modules.inventory_production.domain.expiry_alerts import (
    EXPIRY_ALERT_RULE_KEY,
    ExpiryAlertState,
    ExpiryAlertValidationError,
    acknowledge_alert,
    requires_expiry_alert,
)
from gastroledger_api.technical.cost_projection_models import ControlNotification
from gastroledger_api.technical.inventory_models import (
    InventoryExpiryAlert,
    InventoryLot,
    InventoryStockBalance,
)
from gastroledger_api.technical.postgres_platform import sqlalchemy_database_url


@dataclass(frozen=True)
class ExpiryAlertJob:
    job_id: str
    tenant_id: str
    correlation_id: str


class PostgresExpiryAlertStore:
    def __init__(self, database_url: str) -> None:
        self._database_url = database_url
        self._engine: Engine | None = None

    def _open_session(self) -> Session:
        if self._engine is None:
            self._engine = create_engine(
                sqlalchemy_database_url(self._database_url), poolclass=NullPool
            )
        return Session(self._engine)

    def lease_next(self, worker_id: str) -> ExpiryAlertJob | None:
        with self._open_session() as session, session.begin():
            session.execute(text("set local role gastroledger_app"))
            row = (
                session.execute(
                    text("select * from lease_expiry_alert_job(:worker_id,60)"),
                    {"worker_id": worker_id},
                )
                .mappings()
                .one_or_none()
            )
            return (
                None
                if row is None
                else ExpiryAlertJob(
                    str(row["job_id"]), str(row["tenant_id"]), row["correlation_id"]
                )
            )

    def generate(self, job: ExpiryAlertJob, as_of: date) -> None:
        tenant_id, now = UUID(job.tenant_id), datetime.now(UTC)
        with self._open_session() as session, session.begin():
            self._set_tenant(session, tenant_id)
            rows = session.execute(
                select(InventoryLot, InventoryStockBalance)
                .join(InventoryStockBalance, InventoryStockBalance.lot_id == InventoryLot.id)
                .where(InventoryLot.tenant_id == tenant_id)
            ).all()
            for lot, balance in rows:
                if not requires_expiry_alert(lot.expiry_date, balance.quantity, as_of):
                    continue
                alert_id = uuid4()
                created = session.execute(
                    insert(InventoryExpiryAlert)
                    .values(
                        id=alert_id,
                        tenant_id=tenant_id,
                        warehouse_id=lot.warehouse_id,
                        lot_id=lot.id,
                        expiry_date=lot.expiry_date,
                        rule_key=EXPIRY_ALERT_RULE_KEY,
                        status="active",
                        created_at=now,
                        acknowledged_by=None,
                        acknowledged_at=None,
                        action_note=None,
                    )
                    .on_conflict_do_nothing(index_elements=["tenant_id", "lot_id", "rule_key"])
                    .returning(InventoryExpiryAlert.id)
                ).scalar_one_or_none()
                if created is not None:
                    session.add(
                        ControlNotification(
                            id=uuid4(),
                            tenant_id=tenant_id,
                            source_alert_id=alert_id,
                            recipient_role="branch_operator",
                            title="Lot nearing expiry",
                            body=f"Lot {lot.lot_code} expires on {lot.expiry_date.isoformat()}.",
                            status="active",
                            created_at=now,
                            acknowledged_at=None,
                        )
                    )

    def complete(self, job: ExpiryAlertJob) -> None:
        now = datetime.now(UTC)
        with self._open_session() as session, session.begin():
            self._set_tenant(session, UUID(job.tenant_id))
            session.execute(
                text("""
                update control_jobs set status='queued',available_at=:next_run,
                  lease_until=null,leased_by=null,last_error=null,updated_at=:now
                where id=:job_id and tenant_id=:tenant_id
            """),
                {
                    "job_id": job.job_id,
                    "tenant_id": job.tenant_id,
                    "now": now,
                    "next_run": now + timedelta(days=1),
                },
            )

    def fail(self, job: ExpiryAlertJob, detail: str) -> None:
        now = datetime.now(UTC)
        with self._open_session() as session, session.begin():
            self._set_tenant(session, UUID(job.tenant_id))
            session.execute(
                text("""
                update control_jobs
                set status=case when attempts>=3 then 'failed' else 'queued' end,
                  available_at=:retry_at,lease_until=null,leased_by=null,last_error=:detail,updated_at=:now
                where id=:job_id and tenant_id=:tenant_id
            """),
                {
                    "job_id": job.job_id,
                    "tenant_id": job.tenant_id,
                    "detail": detail[:500],
                    "now": now,
                    "retry_at": now + timedelta(seconds=30),
                },
            )

    def list_expiry_alerts(
        self, identity: ExpiryAlertIdentity, status: str
    ) -> tuple[ExpiryAlertView, ...]:
        with self._open_session() as session, session.begin():
            self._set_tenant(session, UUID(identity.tenant_id))
            rows = session.execute(
                select(InventoryExpiryAlert, InventoryLot.lot_code)
                .join(InventoryLot, InventoryLot.id == InventoryExpiryAlert.lot_id)
                .where(InventoryExpiryAlert.status == status)
                .order_by(InventoryExpiryAlert.expiry_date, InventoryExpiryAlert.created_at)
            ).all()
            return tuple(self._view(alert, lot_code) for alert, lot_code in rows)

    def acknowledge_expiry_alert(
        self,
        identity: ExpiryAlertIdentity,
        alert_id: str,
        action_note: str,
        correlation_id: str,
    ) -> ExpiryAlertView:
        with self._open_session() as session, session.begin():
            self._set_tenant(session, UUID(identity.tenant_id))
            row = session.execute(
                select(InventoryExpiryAlert, InventoryLot.lot_code)
                .join(InventoryLot, InventoryLot.id == InventoryExpiryAlert.lot_id)
                .where(InventoryExpiryAlert.id == UUID(alert_id))
                .with_for_update(of=InventoryExpiryAlert)
            ).one_or_none()
            if row is None:
                raise ExpiryAlertNotFound
            alert, lot_code = row
            try:
                status, note = acknowledge_alert(ExpiryAlertState(alert.status), action_note)
            except ExpiryAlertValidationError as error:
                raise ExpiryAlertConflict from error
            now = datetime.now(UTC)
            alert.status, alert.acknowledged_by, alert.acknowledged_at, alert.action_note = (
                status,
                UUID(identity.actor_id),
                now,
                note,
            )
            notification = session.execute(
                select(ControlNotification).where(ControlNotification.source_alert_id == alert.id)
            ).scalar_one()
            notification.status, notification.acknowledged_at = "acknowledged", now
            session.flush()
            return self._view(alert, lot_code)

    @staticmethod
    def _view(alert: InventoryExpiryAlert, lot_code: str) -> ExpiryAlertView:
        return ExpiryAlertView(
            str(alert.id),
            str(alert.warehouse_id),
            str(alert.lot_id),
            lot_code,
            alert.expiry_date,
            alert.status,
            alert.rule_key,
            alert.created_at,
            str(alert.acknowledged_by) if alert.acknowledged_by else None,
            alert.acknowledged_at,
            alert.action_note,
        )

    @staticmethod
    def _set_tenant(session: Session, tenant_id: UUID) -> None:
        session.execute(text("set local role gastroledger_app"))
        session.execute(
            text("select set_config('app.current_tenant_id',:tenant_id,true)"),
            {"tenant_id": str(tenant_id)},
        )
