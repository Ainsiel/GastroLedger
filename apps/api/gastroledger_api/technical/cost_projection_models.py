from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import (
    JSON,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Integer,
    Numeric,
    Text,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column

from gastroledger_api.technical.platform_models import Base


class ControlOutboxEvent(Base):
    __tablename__ = "control_outbox_events"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("platform_tenants.id"))
    event_type: Mapped[str] = mapped_column(Text)
    aggregate_id: Mapped[UUID] = mapped_column(Uuid)
    payload: Mapped[dict[str, str]] = mapped_column(JSON)
    correlation_id: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(Text)
    attempts: Mapped[int] = mapped_column(Integer)
    available_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_error: Mapped[str | None] = mapped_column(Text)


class ControlJob(Base):
    __tablename__ = "control_jobs"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("platform_tenants.id"))
    job_type: Mapped[str] = mapped_column(Text)
    dedup_key: Mapped[str] = mapped_column(Text)
    payload: Mapped[dict[str, str]] = mapped_column(JSON)
    correlation_id: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(Text)
    attempts: Mapped[int] = mapped_column(Integer)
    available_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    lease_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    leased_by: Mapped[str | None] = mapped_column(Text)
    last_error: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class MenuCostProjectionState(Base):
    __tablename__ = "menu_cost_projection_states"
    __table_args__ = (
        ForeignKeyConstraint(
            ["recipe_version_id", "tenant_id"],
            ["menu_recipe_versions.id", "menu_recipe_versions.tenant_id"],
        ),
    )

    recipe_version_id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("platform_tenants.id"))
    status: Mapped[str] = mapped_column(Text)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    last_error: Mapped[str | None] = mapped_column(Text)


class MenuCostProjectionSnapshot(Base):
    __tablename__ = "menu_cost_projection_snapshots"
    __table_args__ = (
        ForeignKeyConstraint(
            ["recipe_version_id", "tenant_id"],
            ["menu_recipe_versions.id", "menu_recipe_versions.tenant_id"],
        ),
        ForeignKeyConstraint(
            ["source_job_id", "tenant_id"],
            ["control_jobs.id", "control_jobs.tenant_id"],
        ),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("platform_tenants.id"))
    recipe_version_id: Mapped[UUID] = mapped_column(Uuid)
    source_job_id: Mapped[UUID] = mapped_column(Uuid)
    total_cost: Mapped[Decimal] = mapped_column(Numeric(24, 10))
    calculated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
