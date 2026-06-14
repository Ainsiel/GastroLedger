from dataclasses import dataclass

from fastapi import FastAPI

from gastroledger_api.modules.control_insights.public import MODULE_ID as CONTROL_INSIGHTS
from gastroledger_api.modules.inventory_production.public import (
    MODULE_ID as INVENTORY_PRODUCTION,
)
from gastroledger_api.modules.menu_engineering.public import MODULE_ID as MENU_ENGINEERING
from gastroledger_api.modules.platform_organization.public import (
    MODULE_ID as PLATFORM_ORGANIZATION,
)
from gastroledger_api.modules.procurement.public import MODULE_ID as PROCUREMENT
from gastroledger_api.modules.store_operations.public import MODULE_ID as STORE_OPERATIONS
from gastroledger_api.runtime import configure_logging
from gastroledger_api.technical.health import router as health_router


@dataclass(frozen=True)
class ModuleBoundary:
    module_id: str


MODULE_BOUNDARIES = (
    ModuleBoundary(PLATFORM_ORGANIZATION),
    ModuleBoundary(MENU_ENGINEERING),
    ModuleBoundary(PROCUREMENT),
    ModuleBoundary(INVENTORY_PRODUCTION),
    ModuleBoundary(STORE_OPERATIONS),
    ModuleBoundary(CONTROL_INSIGHTS),
)


def create_application() -> FastAPI:
    configure_logging()
    application = FastAPI(title="GastroLedger API", version="0.0.0")
    application.include_router(health_router)
    application.state.module_boundaries = MODULE_BOUNDARIES
    return application

