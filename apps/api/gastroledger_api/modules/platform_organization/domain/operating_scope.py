import re
from dataclasses import dataclass

SUPPORTED_LOCALES = {"en", "es", "pt-br"}
SUPPORTED_BASE_CURRENCIES = {"CLP", "EUR", "USD"}
SUPPORTED_WAREHOUSE_TYPES = {"bar", "general", "kitchen"}
MIN_BRANCH_LIMIT = 1
MAX_BRANCH_LIMIT = 100
CODE_PATTERN = re.compile(r"^[A-Z0-9]+(?:-[A-Z0-9]+)*$")


@dataclass(frozen=True)
class OperatingValidationDetail:
    field: str
    code: str


@dataclass(frozen=True)
class OperatingValidationError(Exception):
    details: tuple[OperatingValidationDetail, ...]


@dataclass(frozen=True)
class ValidatedTenantSettings:
    locale: str
    base_currency: str
    branch_limit: int


@dataclass(frozen=True)
class ValidatedBranch:
    name: str
    code: str


@dataclass(frozen=True)
class ValidatedWarehouse:
    name: str
    code: str
    warehouse_type: str


def _validate_name_and_code(
    *, name: str, code: str
) -> tuple[str, str, list[OperatingValidationDetail]]:
    normalized_name = name.strip()
    normalized_code = code.strip().upper()
    details: list[OperatingValidationDetail] = []
    if not normalized_name or len(normalized_name) > 120:
        details.append(OperatingValidationDetail("name", "invalid"))
    if not CODE_PATTERN.fullmatch(normalized_code) or len(normalized_code) > 63:
        details.append(OperatingValidationDetail("code", "invalid"))
    return normalized_name, normalized_code, details


def validate_branch(*, name: str, code: str) -> ValidatedBranch:
    normalized_name, normalized_code, details = _validate_name_and_code(
        name=name, code=code
    )
    if details:
        raise OperatingValidationError(tuple(details))
    return ValidatedBranch(name=normalized_name, code=normalized_code)


def validate_warehouse(
    *,
    name: str,
    code: str,
    warehouse_type: str,
) -> ValidatedWarehouse:
    normalized_name, normalized_code, details = _validate_name_and_code(
        name=name, code=code
    )
    normalized_type = warehouse_type.strip().lower()
    if normalized_type not in SUPPORTED_WAREHOUSE_TYPES:
        details.append(OperatingValidationDetail("type", "unsupported"))
    if details:
        raise OperatingValidationError(tuple(details))
    return ValidatedWarehouse(
        name=normalized_name,
        code=normalized_code,
        warehouse_type=normalized_type,
    )


def validate_tenant_settings(
    *,
    locale: str,
    base_currency: str,
    branch_limit: int,
) -> ValidatedTenantSettings:
    normalized_locale = locale.strip().lower()
    normalized_currency = base_currency.strip().upper()
    details: list[OperatingValidationDetail] = []

    if normalized_locale not in SUPPORTED_LOCALES:
        details.append(OperatingValidationDetail("locale", "unsupported"))
    if normalized_currency not in SUPPORTED_BASE_CURRENCIES:
        details.append(OperatingValidationDetail("baseCurrency", "unsupported"))
    if type(branch_limit) is not int:
        details.append(OperatingValidationDetail("branchLimit", "invalid_integer"))
    elif not MIN_BRANCH_LIMIT <= branch_limit <= MAX_BRANCH_LIMIT:
        details.append(OperatingValidationDetail("branchLimit", "out_of_range"))

    if details:
        raise OperatingValidationError(tuple(details))

    return ValidatedTenantSettings(
        locale=normalized_locale,
        base_currency=normalized_currency,
        branch_limit=branch_limit,
    )
