from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from gastroledger_api.modules.menu_engineering.domain.catalog import (
    CODE_PATTERN,
    MenuValidationDetail,
    MenuValidationError,
    _parse_positive_decimal,
)

COMPONENT_TYPES = {"ingredient", "sub_recipe"}


@dataclass(frozen=True)
class ValidatedRecipeComponent:
    component_type: str
    component_id: str
    quantity: Decimal
    unit_id: str


@dataclass(frozen=True)
class ValidatedSubRecipeVersion:
    name: str
    code: str
    version: str
    yield_quantity: Decimal
    yield_unit_id: str
    effective_from: date
    components: tuple[ValidatedRecipeComponent, ...]


@dataclass(frozen=True)
class ValidatedMenuItemVersion:
    name: str
    code: str
    version: str
    yield_quantity: Decimal
    yield_unit_id: str
    effective_from: date
    components: tuple[ValidatedRecipeComponent, ...]


@dataclass(frozen=True)
class ValidatedBranchMenuPrice:
    menu_item_version_id: str
    branch_id: str
    price: Decimal
    currency: str
    effective_from: date


def _validate_recipe_version(
    *,
    name: str,
    code: str,
    version: str,
    yield_quantity: str,
    yield_unit_id: str,
    effective_from: date,
    components: tuple[object, ...],
) -> tuple[str, str, str, Decimal, str, tuple[ValidatedRecipeComponent, ...]]:
    details: list[MenuValidationDetail] = []
    normalized_name = name.strip()
    normalized_code = code.strip().upper()
    normalized_version = version.strip()
    normalized_yield_unit = yield_unit_id.strip()
    if not normalized_name or len(normalized_name) > 120:
        details.append(MenuValidationDetail("name", "invalid"))
    if not CODE_PATTERN.fullmatch(normalized_code) or len(normalized_code) > 63:
        details.append(MenuValidationDetail("code", "invalid"))
    if not normalized_version or len(normalized_version) > 40:
        details.append(MenuValidationDetail("version", "invalid"))
    if not normalized_yield_unit:
        details.append(MenuValidationDetail("yieldUnitId", "required"))
    parsed_yield, yield_error = _parse_positive_decimal(
        yield_quantity,
        "yieldQuantity",
    )
    if yield_error:
        details.append(yield_error)
    if not components:
        details.append(MenuValidationDetail("components", "required"))

    validated_components: list[ValidatedRecipeComponent] = []
    for index, component in enumerate(components):
        component_type = str(getattr(component, "component_type", "")).strip()
        component_id = str(getattr(component, "component_id", "")).strip()
        unit_id = str(getattr(component, "unit_id", "")).strip()
        if component_type not in COMPONENT_TYPES:
            details.append(MenuValidationDetail(f"components[{index}].componentType", "invalid"))
        if not component_id:
            details.append(MenuValidationDetail(f"components[{index}].componentId", "required"))
        if not unit_id:
            details.append(MenuValidationDetail(f"components[{index}].unitId", "required"))
        quantity, quantity_error = _parse_positive_decimal(
            str(getattr(component, "quantity", "")),
            f"components[{index}].quantity",
        )
        if quantity_error:
            details.append(quantity_error)
        if component_type in COMPONENT_TYPES and component_id and unit_id and quantity is not None:
            validated_components.append(
                ValidatedRecipeComponent(
                    component_type=component_type,
                    component_id=component_id,
                    quantity=quantity,
                    unit_id=unit_id,
                )
            )
    if details:
        raise MenuValidationError(tuple(details))
    return (
        normalized_name,
        normalized_code,
        normalized_version,
        parsed_yield or Decimal("0"),
        normalized_yield_unit,
        tuple(validated_components),
    )


def validate_sub_recipe_version(
    *,
    name: str,
    code: str,
    version: str,
    yield_quantity: str,
    yield_unit_id: str,
    effective_from: date,
    components: tuple[object, ...],
) -> ValidatedSubRecipeVersion:
    (
        normalized_name,
        normalized_code,
        normalized_version,
        parsed_yield,
        normalized_yield_unit,
        validated_components,
    ) = _validate_recipe_version(
        name=name,
        code=code,
        version=version,
        yield_quantity=yield_quantity,
        yield_unit_id=yield_unit_id,
        effective_from=effective_from,
        components=components,
    )
    return ValidatedSubRecipeVersion(
        name=normalized_name,
        code=normalized_code,
        version=normalized_version,
        yield_quantity=parsed_yield,
        yield_unit_id=normalized_yield_unit,
        effective_from=effective_from,
        components=validated_components,
    )


def validate_menu_item_version(
    *,
    name: str,
    code: str,
    version: str,
    yield_quantity: str,
    yield_unit_id: str,
    effective_from: date,
    components: tuple[object, ...],
) -> ValidatedMenuItemVersion:
    (
        normalized_name,
        normalized_code,
        normalized_version,
        parsed_yield,
        normalized_yield_unit,
        validated_components,
    ) = _validate_recipe_version(
        name=name,
        code=code,
        version=version,
        yield_quantity=yield_quantity,
        yield_unit_id=yield_unit_id,
        effective_from=effective_from,
        components=components,
    )
    return ValidatedMenuItemVersion(
        name=normalized_name,
        code=normalized_code,
        version=normalized_version,
        yield_quantity=parsed_yield,
        yield_unit_id=normalized_yield_unit,
        effective_from=effective_from,
        components=validated_components,
    )


def validate_branch_menu_price(
    *,
    menu_item_version_id: str,
    branch_id: str,
    price: str,
    currency: str,
    effective_from: date,
) -> ValidatedBranchMenuPrice:
    details: list[MenuValidationDetail] = []
    normalized_version_id = menu_item_version_id.strip()
    normalized_branch_id = branch_id.strip()
    normalized_currency = currency.strip().upper()
    if not normalized_version_id:
        details.append(MenuValidationDetail("menuItemVersionId", "required"))
    if not normalized_branch_id:
        details.append(MenuValidationDetail("branchId", "required"))
    if len(normalized_currency) != 3 or not normalized_currency.isalpha():
        details.append(MenuValidationDetail("currency", "invalid"))
    parsed_price, price_error = _parse_positive_decimal(price, "price")
    if price_error:
        details.append(price_error)
    if details:
        raise MenuValidationError(tuple(details))
    return ValidatedBranchMenuPrice(
        menu_item_version_id=normalized_version_id,
        branch_id=normalized_branch_id,
        price=parsed_price or Decimal("0"),
        currency=normalized_currency,
        effective_from=effective_from,
    )
