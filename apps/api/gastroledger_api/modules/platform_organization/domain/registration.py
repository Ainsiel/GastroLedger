import re
from dataclasses import dataclass

SLUG_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@dataclass(frozen=True)
class ValidationDetail:
    field: str
    code: str


@dataclass(frozen=True)
class RegistrationValidationError(Exception):
    details: tuple[ValidationDetail, ...]


@dataclass(frozen=True)
class ValidatedRegistration:
    tenant_name: str
    tenant_slug: str
    admin_email: str
    password: str
    branch_name: str | None
    branch_code: str | None


def validate_registration(
    *,
    tenant_name: str,
    tenant_slug: str,
    admin_email: str,
    password: str,
    branch_name: str | None,
    branch_code: str | None,
) -> ValidatedRegistration:
    normalized_name = tenant_name.strip()
    normalized_slug = tenant_slug.strip().lower()
    normalized_email = admin_email.strip().lower()
    normalized_branch_name = branch_name.strip() if branch_name else None
    normalized_branch_code = branch_code.strip().upper() if branch_code else None
    details: list[ValidationDetail] = []

    if not normalized_name or len(normalized_name) > 120:
        details.append(ValidationDetail("tenantName", "invalid_name"))
    if not SLUG_PATTERN.fullmatch(normalized_slug) or len(normalized_slug) > 63:
        details.append(ValidationDetail("tenantSlug", "invalid_slug"))
    if not EMAIL_PATTERN.fullmatch(normalized_email) or len(normalized_email) > 254:
        details.append(ValidationDetail("adminEmail", "invalid_email"))
    if (
        len(password) < 12
        or len(password) > 128
        or not any(character.islower() for character in password)
        or not any(character.isupper() for character in password)
        or not any(character.isdigit() for character in password)
    ):
        details.append(ValidationDetail("password", "weak_password"))
    if bool(normalized_branch_name) != bool(normalized_branch_code):
        details.append(ValidationDetail("firstBranch", "incomplete_branch"))
    if normalized_branch_name and len(normalized_branch_name) > 120:
        details.append(ValidationDetail("firstBranch.name", "invalid_name"))
    if normalized_branch_code and len(normalized_branch_code) > 63:
        details.append(ValidationDetail("firstBranch.code", "invalid_code"))

    if details:
        raise RegistrationValidationError(tuple(details))

    return ValidatedRegistration(
        tenant_name=normalized_name,
        tenant_slug=normalized_slug,
        admin_email=normalized_email,
        password=password,
        branch_name=normalized_branch_name,
        branch_code=normalized_branch_code,
    )
