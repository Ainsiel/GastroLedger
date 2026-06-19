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
    return ValidatedSubRecipeVersion(
        name=normalized_name,
        code=normalized_code,
        version=normalized_version,
        yield_quantity=parsed_yield or Decimal("0"),
        yield_unit_id=normalized_yield_unit,
        effective_from=effective_from,
        components=tuple(validated_components),
    )
