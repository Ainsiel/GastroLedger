from datetime import UTC, datetime, timedelta

import pytest

from gastroledger_api.modules.platform_organization.public import (
    InvitationExpired,
    InvitationSingleUseViolation,
    InviteLocalUser,
    OperatingAuthorizationDenied,
    OperatingIdentity,
    PrivilegeEscalationDenied,
    UserAccessService,
)


class RecordingUserAccessStore:
    def __init__(self) -> None:
        self.invitation = None
        self.accepted = False

    def create_invitation(self, identity, invitation, token_hash, expires_at, correlation_id):
        self.invitation = (identity, invitation, token_hash, expires_at, correlation_id)
        return {
            "invitationId": "invitation-1",
            "manualShareToken": "raw-token",
            "inviteeLogin": invitation.invitee_login,
            "role": invitation.role,
            "scope": invitation.scope,
            "branchId": invitation.branch_id,
            "expiresAt": expires_at,
            "status": "pending",
        }

    def accept_invitation(self, command, token_hash, password_hash, correlation_id):
        self.accepted = True
        return {
            "tenantId": "tenant-1",
            "actorId": "actor-2",
            "tenantName": "Tenant",
            "tenantSlug": "tenant",
            "sessionToken": "session-token",
        }

    def list_visible_branches(self, identity):
        if identity.branch_ids:
            return ("branch-1",)
        return ("branch-1", "branch-2")


def test_tenant_admin_generates_a_time_limited_branch_scoped_invitation() -> None:
    store = RecordingUserAccessStore()
    service = UserAccessService(store=store)
    identity = OperatingIdentity(
        tenant_id="tenant-1",
        actor_id="admin-1",
        role="tenant_admin",
        branch_ids=(),
    )

    invitation = service.invite_local_user(
        identity,
        InviteLocalUser(
            invitee_login=" Manager@Example.com ",
            role="branch_manager",
            scope="branch",
            branch_id="branch-1",
            ttl_hours=24,
        ),
        correlation_id="invite-1",
    )

    assert invitation["inviteeLogin"] == "manager@example.com"
    assert invitation["role"] == "branch_manager"
    assert invitation["scope"] == "branch"
    assert invitation["branchId"] == "branch-1"
    assert invitation["manualShareToken"]
    assert store.invitation[0] == identity
    assert store.invitation[3] > datetime.now(UTC)


def test_non_admin_and_privilege_escalation_do_not_create_invitations() -> None:
    service = UserAccessService(store=RecordingUserAccessStore())

    with pytest.raises(OperatingAuthorizationDenied):
        service.invite_local_user(
            OperatingIdentity(
                tenant_id="tenant-1",
                actor_id="actor-1",
                role="branch_manager",
                branch_ids=("branch-1",),
            ),
            InviteLocalUser(
                invitee_login="new@example.com",
                role="branch_operator",
                scope="branch",
                branch_id="branch-1",
                ttl_hours=24,
            ),
            correlation_id="invite-forbidden",
        )

    with pytest.raises(PrivilegeEscalationDenied):
        service.invite_local_user(
            OperatingIdentity(
                tenant_id="tenant-1",
                actor_id="admin-1",
                role="tenant_admin",
                branch_ids=(),
            ),
            InviteLocalUser(
                invitee_login="new@example.com",
                role="tenant_admin",
                scope="tenant",
                branch_id=None,
                ttl_hours=24,
            ),
            correlation_id="invite-escalation",
        )


def test_expired_and_used_invitations_are_rejected_before_session_creation() -> None:
    service = UserAccessService(store=RecordingUserAccessStore())

    with pytest.raises(InvitationExpired):
        service.ensure_invitation_usable(
            expires_at=datetime.now(UTC) - timedelta(minutes=1),
            accepted_at=None,
        )

    with pytest.raises(InvitationSingleUseViolation):
        service.ensure_invitation_usable(
            expires_at=datetime.now(UTC) + timedelta(minutes=1),
            accepted_at=datetime.now(UTC),
        )


def test_branch_scoped_identity_only_sees_assigned_branches() -> None:
    service = UserAccessService(store=RecordingUserAccessStore())

    visible = service.list_visible_branches(
        OperatingIdentity(
            tenant_id="tenant-1",
            actor_id="actor-2",
            role="branch_manager",
            branch_ids=("branch-1",),
        )
    )

    assert visible == ("branch-1",)
