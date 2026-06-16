import re
from dataclasses import dataclass

SUPPORTED_INVITATION_ROLES = {
    "branch_manager",
    "branch_operator",
    "tenant_operator",
    "tenant_admin",
}
SUPPORTED_INVITATION_SCOPES = {"branch", "tenant"}
MAX_INVITATION_TTL_HOURS = 168
LOGIN_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@dataclass(frozen=True)
class UserAccessValidationDetail:
    field: str
    code: str


@dataclass(frozen=True)
class UserAccessValidationError(Exception):
    details: tuple[UserAccessValidationDetail, ...]


@dataclass(frozen=True)
class ValidatedInvitation:
    invitee_login: str
    role: str
    scope: str
    branch_id: str | None
    ttl_hours: int


def validate_invitation(
    *,
    invitee_login: str,
    role: str,
    scope: str,
    branch_id: str | None,
    ttl_hours: int,
) -> ValidatedInvitation:
    normalized_login = invitee_login.strip().lower()
    normalized_role = role.strip().lower()
    normalized_scope = scope.strip().lower()
    normalized_branch_id = branch_id.strip() if branch_id else None
    details: list[UserAccessValidationDetail] = []

    if not LOGIN_PATTERN.fullmatch(normalized_login) or len(normalized_login) > 254:
        details.append(UserAccessValidationDetail("inviteeLogin", "invalid"))
    if normalized_role not in SUPPORTED_INVITATION_ROLES:
        details.append(UserAccessValidationDetail("role", "unsupported"))
    if normalized_scope not in SUPPORTED_INVITATION_SCOPES:
        details.append(UserAccessValidationDetail("scope", "unsupported"))
    if normalized_scope == "branch" and not normalized_branch_id:
        details.append(UserAccessValidationDetail("branchId", "required"))
    if normalized_scope == "tenant" and normalized_branch_id:
        details.append(UserAccessValidationDetail("branchId", "not_allowed"))
    if type(ttl_hours) is not int or not 1 <= ttl_hours <= MAX_INVITATION_TTL_HOURS:
        details.append(UserAccessValidationDetail("ttlHours", "out_of_range"))

    if details:
        raise UserAccessValidationError(tuple(details))

    return ValidatedInvitation(
        invitee_login=normalized_login,
        role=normalized_role,
        scope=normalized_scope,
        branch_id=normalized_branch_id,
        ttl_hours=ttl_hours,
    )
