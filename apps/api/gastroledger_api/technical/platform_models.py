from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, ForeignKeyConstraint, Integer, Text, Uuid
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class PlatformTenant(Base):
    __tablename__ = "platform_tenants"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    slug: Mapped[str] = mapped_column(Text, unique=True)
    name: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class PlatformTenantSetting(Base):
    __tablename__ = "platform_tenant_settings"

    tenant_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("platform_tenants.id"), primary_key=True
    )
    locale: Mapped[str] = mapped_column(Text)
    base_currency: Mapped[str] = mapped_column(Text)
    branch_limit: Mapped[int] = mapped_column(Integer)


class PlatformUser(Base):
    __tablename__ = "platform_users"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    normalized_login: Mapped[str] = mapped_column(Text, unique=True)
    password_hash: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class PlatformMembership(Base):
    __tablename__ = "platform_memberships"

    tenant_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("platform_tenants.id"), primary_key=True
    )
    user_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("platform_users.id"), primary_key=True
    )
    role: Mapped[str] = mapped_column(Text)


class PlatformMembershipRole(Base):
    __tablename__ = "platform_membership_roles"
    __table_args__ = (
        ForeignKeyConstraint(
            ["tenant_id", "user_id"],
            ["platform_memberships.tenant_id", "platform_memberships.user_id"],
        ),
        ForeignKeyConstraint(
            ["branch_id", "tenant_id"],
            ["platform_branches.id", "platform_branches.tenant_id"],
        ),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("platform_tenants.id"))
    user_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("platform_users.id"))
    role: Mapped[str] = mapped_column(Text)
    scope: Mapped[str] = mapped_column(Text)
    branch_id: Mapped[UUID | None] = mapped_column(Uuid)


class PlatformBranch(Base):
    __tablename__ = "platform_branches"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("platform_tenants.id"))
    code: Mapped[str] = mapped_column(Text)
    name: Mapped[str] = mapped_column(Text)


class PlatformWarehouse(Base):
    __tablename__ = "platform_warehouses"
    __table_args__ = (
        ForeignKeyConstraint(
            ["branch_id", "tenant_id"],
            ["platform_branches.id", "platform_branches.tenant_id"],
        ),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("platform_tenants.id"))
    branch_id: Mapped[UUID] = mapped_column(Uuid)
    code: Mapped[str] = mapped_column(Text)
    name: Mapped[str] = mapped_column(Text)
    type: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(Text)


class PlatformInvitation(Base):
    __tablename__ = "platform_invitations"
    __table_args__ = (
        ForeignKeyConstraint(
            ["branch_id", "tenant_id"],
            ["platform_branches.id", "platform_branches.tenant_id"],
        ),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("platform_tenants.id"))
    invitee_login: Mapped[str] = mapped_column(Text)
    token_hash: Mapped[str] = mapped_column(Text, unique=True)
    role: Mapped[str] = mapped_column(Text)
    scope: Mapped[str] = mapped_column(Text)
    branch_id: Mapped[UUID | None] = mapped_column(Uuid)
    created_by: Mapped[UUID] = mapped_column(Uuid, ForeignKey("platform_users.id"))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    accepted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
class PlatformSession(Base):
    __tablename__ = "platform_sessions"
    __table_args__ = (
        ForeignKeyConstraint(
            ["tenant_id", "user_id"],
            ["platform_memberships.tenant_id", "platform_memberships.user_id"],
        ),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("platform_tenants.id"))
    user_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("platform_users.id"))
    token_hash: Mapped[str] = mapped_column(Text, unique=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class ControlAuditEvent(Base):
    __tablename__ = "control_audit_events"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("platform_tenants.id"))
    actor_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("platform_users.id"))
    correlation_id: Mapped[str] = mapped_column(Text)
    action: Mapped[str] = mapped_column(Text)
    object_reference: Mapped[str] = mapped_column(Text)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
