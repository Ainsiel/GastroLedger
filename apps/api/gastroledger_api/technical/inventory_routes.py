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
    RequestTransfer,
    SubmitWaste,
    TransferAuthorizationDenied,
    TransferConflict,
    TransferIdentity,
    TransferInsufficientStock,
    TransferNotFound,
    TransferService,
    TransferValidationError,
    TransferView,
    WasteAuthorizationDenied,
    WasteConflict,
    WasteIdentity,
    WasteInsufficientStock,
    WasteNotFound,
    WasteService,
    WasteValidationError,
    WasteView,
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


class TransferRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    transferNumber: str
    sourceWarehouseId: str
    destinationWarehouseId: str
    itemType: str
    itemId: str
    unitId: str
    requestedQuantity: str


class TransferApprovalRequest(BaseModel):
    approvedQuantity: str


class TransferDispatchRequest(BaseModel):
    dispatchQuantity: str


class TransferReceiptRequest(BaseModel):
    receivedQuantity: str
    lossQuantity: str = "0"
    lossReason: str = ""


class TransferResponse(BaseModel):
    transferId: str
    transferNumber: str
    status: str
    sourceWarehouseId: str
    destinationWarehouseId: str
    itemType: str
    itemId: str
    unitId: str
    requestedQuantity: str
    approvedQuantity: str
    dispatchedQuantity: str
    receivedQuantity: str
    lossQuantity: str


class WasteSubmissionRequest(BaseModel):
    warehouseId: str
    lotId: str
    quantity: str
    reason: str


class WasteDecisionRequest(BaseModel):
    reason: str = ""


class WasteResponse(BaseModel):
    wasteId: str
    status: str
    warehouseId: str
    lotId: str
    quantity: str
    operationalValue: str
    reason: str
    requestedBy: str
    decisionBy: str | None
    inventoryTransactionId: str | None


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


def transfer_response(value: TransferView) -> TransferResponse:
    def amount(number):
        return format(number.normalize(), "f")

    return TransferResponse(
        transferId=value.transfer_id,
        transferNumber=value.transfer_number,
        status=value.status,
        sourceWarehouseId=value.source_warehouse_id,
        destinationWarehouseId=value.destination_warehouse_id,
        itemType=value.item_type,
        itemId=value.item_id,
        unitId=value.unit_id,
        requestedQuantity=amount(value.requested_quantity),
        approvedQuantity=amount(value.approved_quantity),
        dispatchedQuantity=amount(value.dispatched_quantity),
        receivedQuantity=amount(value.received_quantity),
        lossQuantity=amount(value.loss_quantity),
    )


def waste_response(value: WasteView) -> WasteResponse:
    def amount(number):
        return format(number.normalize(), "f")

    return WasteResponse(
        wasteId=value.waste_id,
        status=value.status,
        warehouseId=value.warehouse_id,
        lotId=value.lot_id,
        quantity=amount(value.quantity),
        operationalValue=amount(value.operational_value),
        reason=value.reason,
        requestedBy=value.requested_by,
        decisionBy=value.decision_by,
        inventoryTransactionId=value.inventory_transaction_id,
    )


def create_inventory_router(database_url: str | None = None) -> APIRouter:
    router = APIRouter(prefix="/api/v1/inventory", tags=["inventory-production"])
    resolved_database_url = database_url or os.environ.get("DATABASE_URL", "")
    platform_store = PostgresPlatformStore(resolved_database_url)
    service = ProductionService(store=PostgresInventoryStore(resolved_database_url))
    transfers = TransferService(store=PostgresInventoryStore(resolved_database_url))
    waste = WasteService(store=PostgresInventoryStore(resolved_database_url))

    def identity(gl_session: str | None) -> ProductionIdentity:
        if not gl_session:
            raise AuthenticationRequired
        operating = platform_store.resolve_operating_identity(gl_session)
        return ProductionIdentity(operating.tenant_id, operating.actor_id, operating.role)

    def transfer_identity(gl_session: str | None) -> TransferIdentity:
        value = identity(gl_session)
        return TransferIdentity(value.tenant_id, value.actor_id, value.role)

    def waste_identity(gl_session: str | None) -> WasteIdentity:
        value = identity(gl_session)
        return WasteIdentity(value.tenant_id, value.actor_id, value.role)

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
        if isinstance(error, TransferAuthorizationDenied):
            return problem_response(
                403, "inventory.transfer_authorization_denied", correlation_id, []
            )
        if isinstance(error, TransferNotFound):
            return problem_response(404, "inventory.transfer_not_found", correlation_id, [])
        if isinstance(error, TransferInsufficientStock):
            return problem_response(
                409, "inventory.transfer_insufficient_stock", correlation_id, []
            )
        if isinstance(error, TransferConflict):
            return problem_response(409, "inventory.transfer_conflict", correlation_id, [])
        if isinstance(error, TransferValidationError):
            return problem_response(
                422,
                "inventory.transfer_invalid",
                correlation_id,
                [
                    {"field": detail.field, "code": detail.code, "detail": "review field"}
                    for detail in error.details
                ],
            )
        if isinstance(error, WasteAuthorizationDenied):
            return problem_response(403, "inventory.waste_authorization_denied", correlation_id, [])
        if isinstance(error, WasteNotFound):
            return problem_response(404, "inventory.waste_not_found", correlation_id, [])
        if isinstance(error, WasteInsufficientStock):
            return problem_response(409, "inventory.waste_insufficient_stock", correlation_id, [])
        if isinstance(error, WasteConflict):
            return problem_response(409, "inventory.waste_conflict", correlation_id, [])
        if isinstance(error, WasteValidationError):
            return problem_response(
                422,
                "inventory.waste_invalid",
                correlation_id,
                [
                    {"field": detail.field, "code": detail.code, "detail": "review field"}
                    for detail in error.details
                ],
            )
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

    transfer_errors = (
        AuthenticationRequired,
        TransferAuthorizationDenied,
        TransferNotFound,
        TransferInsufficientStock,
        TransferConflict,
        TransferValidationError,
        ValueError,
        psycopg.Error,
        SQLAlchemyError,
    )

    @router.post("/transfers", response_model=TransferResponse, status_code=201)
    def request_transfer(
        request: TransferRequest, gl_session: str | None = Security(session_cookie)
    ):
        correlation_id = str(uuid4())
        try:
            return transfer_response(
                transfers.request_transfer(
                    transfer_identity(gl_session),
                    RequestTransfer(
                        request.transferNumber,
                        request.sourceWarehouseId,
                        request.destinationWarehouseId,
                        request.itemType,
                        request.itemId,
                        request.unitId,
                        request.requestedQuantity,
                    ),
                    correlation_id=correlation_id,
                )
            )
        except transfer_errors as error:
            return inventory_problem(error, correlation_id)

    @router.post("/transfers/{transferId}/approve", response_model=TransferResponse)
    def approve_transfer_route(
        transferId: str,
        request: TransferApprovalRequest,
        gl_session: str | None = Security(session_cookie),
    ):
        correlation_id = str(uuid4())
        try:
            return transfer_response(
                transfers.approve_transfer(
                    transfer_identity(gl_session),
                    transferId,
                    request.approvedQuantity,
                    correlation_id=correlation_id,
                )
            )
        except transfer_errors as error:
            return inventory_problem(error, correlation_id)

    @router.post("/transfers/{transferId}/dispatch/{commandId}", response_model=TransferResponse)
    def dispatch_transfer_route(
        transferId: str,
        commandId: str,
        request: TransferDispatchRequest,
        gl_session: str | None = Security(session_cookie),
    ):
        correlation_id = str(uuid4())
        try:
            return transfer_response(
                transfers.dispatch_transfer(
                    transfer_identity(gl_session),
                    transferId,
                    commandId,
                    request.dispatchQuantity,
                    correlation_id=correlation_id,
                )
            )
        except transfer_errors as error:
            return inventory_problem(error, correlation_id)

    @router.post("/transfers/{transferId}/receive/{commandId}", response_model=TransferResponse)
    def receive_transfer_route(
        transferId: str,
        commandId: str,
        request: TransferReceiptRequest,
        gl_session: str | None = Security(session_cookie),
    ):
        correlation_id = str(uuid4())
        try:
            return transfer_response(
                transfers.receive_transfer(
                    transfer_identity(gl_session),
                    transferId,
                    commandId,
                    request.receivedQuantity,
                    request.lossQuantity,
                    request.lossReason,
                    correlation_id=correlation_id,
                )
            )
        except transfer_errors as error:
            return inventory_problem(error, correlation_id)

    waste_errors = (
        AuthenticationRequired,
        WasteAuthorizationDenied,
        WasteNotFound,
        WasteInsufficientStock,
        WasteConflict,
        WasteValidationError,
        ValueError,
        psycopg.Error,
        SQLAlchemyError,
    )

    @router.post("/waste/commands/{commandId}", response_model=WasteResponse, status_code=201)
    def submit_waste_route(
        commandId: str,
        request: WasteSubmissionRequest,
        gl_session: str | None = Security(session_cookie),
    ):
        correlation_id = str(uuid4())
        try:
            return waste_response(
                waste.submit_waste(
                    waste_identity(gl_session),
                    SubmitWaste(
                        commandId,
                        request.warehouseId,
                        request.lotId,
                        request.quantity,
                        request.reason,
                    ),
                    correlation_id=correlation_id,
                )
            )
        except waste_errors as error:
            return inventory_problem(error, correlation_id)

    @router.post("/waste/{wasteId}/approve/{commandId}", response_model=WasteResponse)
    def approve_waste_route(
        wasteId: str, commandId: str, gl_session: str | None = Security(session_cookie)
    ):
        correlation_id = str(uuid4())
        try:
            return waste_response(
                waste.approve_waste(
                    waste_identity(gl_session), wasteId, commandId, correlation_id=correlation_id
                )
            )
        except waste_errors as error:
            return inventory_problem(error, correlation_id)

    @router.post("/waste/{wasteId}/reject", response_model=WasteResponse)
    def reject_waste_route(
        wasteId: str,
        request: WasteDecisionRequest,
        gl_session: str | None = Security(session_cookie),
    ):
        correlation_id = str(uuid4())
        try:
            return waste_response(
                waste.reject_waste(
                    waste_identity(gl_session),
                    wasteId,
                    request.reason,
                    correlation_id=correlation_id,
                )
            )
        except waste_errors as error:
            return inventory_problem(error, correlation_id)

    @router.post("/waste/{wasteId}/correct/{commandId}", response_model=WasteResponse)
    def correct_waste_route(
        wasteId: str,
        commandId: str,
        request: WasteDecisionRequest,
        gl_session: str | None = Security(session_cookie),
    ):
        correlation_id = str(uuid4())
        try:
            return waste_response(
                waste.correct_waste(
                    waste_identity(gl_session),
                    wasteId,
                    commandId,
                    request.reason,
                    correlation_id=correlation_id,
                )
            )
        except waste_errors as error:
            return inventory_problem(error, correlation_id)

    return router
