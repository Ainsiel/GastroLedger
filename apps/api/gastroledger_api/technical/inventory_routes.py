import os
from datetime import date
from uuid import uuid4

import psycopg
from fastapi import APIRouter, Security
from fastapi.security import APIKeyCookie
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.exc import SQLAlchemyError

from gastroledger_api.modules.inventory_production.public import (
    PostProductionBatch,
    ProductionAuthorizationDenied,
    ProductionBatchView,
    ProductionConflict,
    ProductionIdentity,
    ProductionInsufficientStock,
    ProductionNotFound,
    ProductionService,
    ProductionValidationError,
)
from gastroledger_api.modules.platform_organization.public import AuthenticationRequired
from gastroledger_api.technical.postgres_inventory import PostgresInventoryStore
from gastroledger_api.technical.postgres_platform import PostgresPlatformStore
from gastroledger_api.technical.problems import ApiProblem, problem_response

session_cookie = APIKeyCookie(name="gl_session", auto_error=False)

INVENTORY_RESPONSES = {
    401: {"model": ApiProblem, "description": "A valid local session is required."},
    403: {"model": ApiProblem, "description": "Production access is required."},
    404: {"model": ApiProblem, "description": "The recipe or warehouse is not visible."},
    409: {"model": ApiProblem, "description": "The production command conflicts."},
    422: {"model": ApiProblem, "description": "The production input is invalid."},
    500: {"model": ApiProblem, "description": "The command could not be completed."},
}


class ProductionBatchRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    batchNumber: str = Field(min_length=1, max_length=80)
    warehouseId: str = Field(min_length=1)
    recipeVersionId: str = Field(min_length=1)
    actualYield: str = Field(min_length=1, max_length=50)
    outputLotCode: str = Field(min_length=1, max_length=80)
    producedOn: date
    varianceReason: str = Field(default="", max_length=240)


class ProductionBatchResponse(BaseModel):
    productionBatchId: str
    inventoryTransactionId: str
    outputLotId: str
    batchNumber: str
    status: str
    recipeVersionId: str
    expectedYield: str
    actualYield: str
    varianceQuantity: str
    varianceReason: str | None
    consumedQuantity: str


def production_response(batch: ProductionBatchView) -> ProductionBatchResponse:
    return ProductionBatchResponse(
        productionBatchId=batch.production_batch_id,
        inventoryTransactionId=batch.inventory_transaction_id,
        outputLotId=batch.output_lot_id,
        batchNumber=batch.batch_number,
        status=batch.status,
        recipeVersionId=batch.recipe_version_id,
        expectedYield=format(batch.expected_yield.normalize(), "f"),
        actualYield=format(batch.actual_yield.normalize(), "f"),
        varianceQuantity=format(batch.variance_quantity.normalize(), "f"),
        varianceReason=batch.variance_reason,
        consumedQuantity=format(batch.consumed_quantity.normalize(), "f"),
    )


def create_inventory_router(database_url: str | None = None) -> APIRouter:
    router = APIRouter(prefix="/api/v1/inventory", tags=["inventory-production"])
    resolved_database_url = database_url or os.environ.get("DATABASE_URL", "")
    platform_store = PostgresPlatformStore(resolved_database_url)
    service = ProductionService(store=PostgresInventoryStore(resolved_database_url))

    def identity(gl_session: str | None) -> ProductionIdentity:
        if not gl_session:
            raise AuthenticationRequired
        operating = platform_store.resolve_operating_identity(gl_session)
        return ProductionIdentity(operating.tenant_id, operating.actor_id, operating.role)

    def inventory_problem(error: Exception, correlation_id: str):
        if isinstance(error, AuthenticationRequired):
            return problem_response(401, "inventory.authentication_required", correlation_id, [])
        if isinstance(error, ProductionAuthorizationDenied):
            return problem_response(403, "inventory.authorization_denied", correlation_id, [])
        if isinstance(error, ProductionNotFound):
            return problem_response(
                404, "inventory.production_reference_not_found", correlation_id, []
            )
        if isinstance(error, ProductionInsufficientStock):
            return problem_response(409, "inventory.insufficient_stock", correlation_id, [])
        if isinstance(error, ProductionConflict):
            return problem_response(409, "inventory.production_conflict", correlation_id, [])
        if isinstance(error, ProductionValidationError):
            return problem_response(
                422,
                "inventory.production_invalid",
                correlation_id,
                [
                    {"field": detail.field, "code": detail.code, "detail": "review field"}
                    for detail in error.details
                ],
            )
        return problem_response(500, "inventory.command_failed", correlation_id, [])

    @router.post(
        "/production-batches/{batchId}/post",
        response_model=ProductionBatchResponse,
        status_code=201,
        operation_id="postProductionBatch",
        summary="Post a production batch to the immutable inventory ledger",
        responses=INVENTORY_RESPONSES,
    )
    def post_production_batch(
        batchId: str,
        request: ProductionBatchRequest,
        gl_session: str | None = Security(session_cookie),
    ):
        correlation_id = str(uuid4())
        try:
            return production_response(
                service.post_batch(
                    identity(gl_session),
                    PostProductionBatch(
                        idempotency_key=batchId,
                        batch_number=request.batchNumber,
                        warehouse_id=request.warehouseId,
                        recipe_version_id=request.recipeVersionId,
                        actual_yield=request.actualYield,
                        output_lot_code=request.outputLotCode,
                        produced_on=request.producedOn,
                        variance_reason=request.varianceReason,
                    ),
                    correlation_id=correlation_id,
                )
            )
        except (
            AuthenticationRequired,
            ProductionAuthorizationDenied,
            ProductionNotFound,
            ProductionInsufficientStock,
            ProductionConflict,
            ProductionValidationError,
            ValueError,
            psycopg.Error,
            SQLAlchemyError,
        ) as error:
            return inventory_problem(error, correlation_id)

    return router
