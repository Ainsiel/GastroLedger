import os
from datetime import date
from uuid import uuid4

import psycopg
from fastapi import APIRouter, Security
from fastapi.security import APIKeyCookie
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.exc import SQLAlchemyError

from gastroledger_api.modules.platform_organization.public import AuthenticationRequired
from gastroledger_api.modules.procurement.public import (
    CreateSupplier,
    CreateSupplierOffer,
    CreateSupplierReceipt,
    CreateSupplierReceiptLine,
    ProcurementAuthorizationDenied,
    ProcurementCodeConflict,
    ProcurementDateOverlap,
    ProcurementNotFound,
    ProcurementReceiptService,
    ProcurementService,
    ProcurementUnitMismatch,
    ProcurementValidationError,
    SupplierIdentity,
    SupplierOfferView,
    SupplierReceiptLineView,
    SupplierReceiptView,
    SupplierView,
)
from gastroledger_api.technical.postgres_platform import PostgresPlatformStore
from gastroledger_api.technical.postgres_procurement import PostgresProcurementStore
from gastroledger_api.technical.problems import ApiProblem, problem_response

SESSION_COOKIE = "gl_session"
session_cookie = APIKeyCookie(
    name=SESSION_COOKIE,
    auto_error=False,
    description="Opaque local session cookie issued after tenant registration or login.",
)

PROCUREMENT_RESPONSES = {
    401: {"model": ApiProblem, "description": "A valid local session is required."},
    403: {"model": ApiProblem, "description": "Procurement access is required."},
    404: {"model": ApiProblem, "description": "The scoped procurement resource is not visible."},
    409: {"model": ApiProblem, "description": "The procurement command conflicts."},
    422: {"model": ApiProblem, "description": "The procurement input is invalid."},
    500: {"model": ApiProblem, "description": "The command could not be completed."},
}


class SupplierRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=120)
    code: str = Field(min_length=1, max_length=63)


class SupplierOfferRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    supplierId: str = Field(min_length=1)
    ingredientId: str = Field(min_length=1)
    purchaseUnitId: str = Field(min_length=1)
    price: str = Field(min_length=1, max_length=50)
    currency: str = Field(min_length=3, max_length=3)
    effectiveFrom: date
    effectiveUntil: date | None = None


class SupplierReceiptLineRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ingredientId: str = Field(min_length=1)
    purchaseUnitId: str = Field(min_length=1)
    lotCode: str = Field(min_length=1, max_length=80)
    orderedQuantity: str = Field(min_length=1, max_length=50)
    deliveredQuantity: str = Field(min_length=1, max_length=50)
    unitCost: str = Field(min_length=1, max_length=50)
    expiryDate: date
    temperature: str = Field(min_length=1, max_length=30)
    minimumTemperature: str = Field(min_length=1, max_length=30)
    maximumTemperature: str = Field(min_length=1, max_length=30)
    tolerancePercent: str = Field(min_length=1, max_length=30)


class SupplierReceiptRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    orderReference: str = Field(min_length=1, max_length=120)
    supplierId: str = Field(min_length=1)
    warehouseId: str = Field(min_length=1)
    receivedOn: date
    lines: list[SupplierReceiptLineRequest] = Field(min_length=1)


class SupplierResponse(BaseModel):
    supplierId: str
    name: str
    code: str
    status: str


class SupplierOfferResponse(BaseModel):
    supplierOfferId: str
    supplierId: str
    ingredientId: str
    purchaseUnitId: str
    price: str
    currency: str
    effectiveFrom: date
    effectiveUntil: date | None


class SupplierReceiptLineResponse(BaseModel):
    receiptLineId: str
    lotId: str | None
    lotCode: str
    acceptedQuantity: str
    remainingQuantity: str
    status: str
    rejectionReason: str | None


class SupplierReceiptResponse(BaseModel):
    receiptId: str
    inventoryTransactionId: str | None
    idempotencyKey: str
    orderReference: str
    status: str
    lines: list[SupplierReceiptLineResponse]


def supplier_response(supplier: SupplierView) -> SupplierResponse:
    return SupplierResponse(
        supplierId=supplier.supplier_id,
        name=supplier.name,
        code=supplier.code,
        status=supplier.status,
    )


def offer_response(offer: SupplierOfferView) -> SupplierOfferResponse:
    return SupplierOfferResponse(
        supplierOfferId=offer.supplier_offer_id,
        supplierId=offer.supplier_id,
        ingredientId=offer.ingredient_id,
        purchaseUnitId=offer.purchase_unit_id,
        price=format(offer.price.normalize(), "f"),
        currency=offer.currency,
        effectiveFrom=offer.effective_from,
        effectiveUntil=offer.effective_until,
    )


def receipt_line_response(line: SupplierReceiptLineView) -> SupplierReceiptLineResponse:
    return SupplierReceiptLineResponse(
        receiptLineId=line.receipt_line_id,
        lotId=line.lot_id,
        lotCode=line.lot_code,
        acceptedQuantity=format(line.accepted_quantity.normalize(), "f"),
        remainingQuantity=format(line.remaining_quantity.normalize(), "f"),
        status=line.status,
        rejectionReason=line.rejection_reason,
    )


def receipt_response(receipt: SupplierReceiptView) -> SupplierReceiptResponse:
    return SupplierReceiptResponse(
        receiptId=receipt.receipt_id,
        inventoryTransactionId=receipt.inventory_transaction_id,
        idempotencyKey=receipt.idempotency_key,
        orderReference=receipt.order_reference,
        status=receipt.status,
        lines=[receipt_line_response(line) for line in receipt.lines],
    )


def create_procurement_router(database_url: str | None = None) -> APIRouter:
    router = APIRouter(prefix="/api/v1/procurement", tags=["procurement"])
    resolved_database_url = database_url or os.environ.get("DATABASE_URL", "")
    platform_store = PostgresPlatformStore(resolved_database_url)
    service = ProcurementService(store=PostgresProcurementStore(resolved_database_url))
    receipts = ProcurementReceiptService(
        store=PostgresProcurementStore(resolved_database_url)
    )

    def procurement_identity(gl_session: str | None) -> SupplierIdentity:
        if not gl_session:
            raise AuthenticationRequired
        identity = platform_store.resolve_operating_identity(gl_session)
        return SupplierIdentity(
            tenant_id=identity.tenant_id,
            actor_id=identity.actor_id,
            role=identity.role,
        )

    def procurement_problem(error: Exception, correlation_id: str):
        if isinstance(error, AuthenticationRequired):
            return problem_response(401, "procurement.authentication_required", correlation_id, [])
        if isinstance(error, ProcurementAuthorizationDenied):
            return problem_response(403, "procurement.authorization_denied", correlation_id, [])
        if isinstance(error, ProcurementNotFound):
            return problem_response(404, "procurement.not_found", correlation_id, [])
        if isinstance(error, ProcurementValidationError):
            return problem_response(
                422,
                "procurement.invalid",
                correlation_id,
                [
                    {"field": detail.field, "code": detail.code, "detail": "review field"}
                    for detail in error.details
                ],
            )
        if isinstance(error, ProcurementUnitMismatch):
            return problem_response(
                422,
                "procurement.purchase_unit_mismatch",
                correlation_id,
                [{"field": "purchaseUnitId", "code": "mismatch", "detail": "review unit"}],
            )
        if isinstance(error, ProcurementDateOverlap):
            return problem_response(409, "procurement.offer_overlap", correlation_id, [])
        if isinstance(error, ProcurementCodeConflict):
            return problem_response(409, "procurement.code_conflict", correlation_id, [])
        return problem_response(500, "procurement.command_failed", correlation_id, [])

    @router.get(
        "/suppliers",
        response_model=list[SupplierResponse],
        operation_id="listProcurementSuppliers",
        summary="List tenant suppliers",
        responses=PROCUREMENT_RESPONSES,
    )
    def list_suppliers(gl_session: str | None = Security(session_cookie)):
        correlation_id = str(uuid4())
        try:
            return [
                supplier_response(supplier)
                for supplier in service.list_suppliers(procurement_identity(gl_session))
            ]
        except (
            AuthenticationRequired,
            ProcurementAuthorizationDenied,
            psycopg.Error,
            SQLAlchemyError,
        ) as error:
            return procurement_problem(error, correlation_id)

    @router.post(
        "/suppliers",
        response_model=SupplierResponse,
        status_code=201,
        operation_id="createProcurementSupplier",
        summary="Create a tenant supplier",
        responses=PROCUREMENT_RESPONSES,
    )
    def create_supplier(
        request: SupplierRequest,
        gl_session: str | None = Security(session_cookie),
    ):
        correlation_id = str(uuid4())
        try:
            return supplier_response(
                service.create_supplier(
                    procurement_identity(gl_session),
                    CreateSupplier(name=request.name, code=request.code),
                    correlation_id=correlation_id,
                )
            )
        except (
            AuthenticationRequired,
            ProcurementAuthorizationDenied,
            ProcurementValidationError,
            ProcurementCodeConflict,
            psycopg.Error,
            SQLAlchemyError,
        ) as error:
            return procurement_problem(error, correlation_id)

    @router.get(
        "/offers",
        response_model=list[SupplierOfferResponse],
        operation_id="listProcurementSupplierOffers",
        summary="List tenant supplier offers",
        responses=PROCUREMENT_RESPONSES,
    )
    def list_offers(gl_session: str | None = Security(session_cookie)):
        correlation_id = str(uuid4())
        try:
            return [
                offer_response(offer)
                for offer in service.list_offers(procurement_identity(gl_session))
            ]
        except (
            AuthenticationRequired,
            ProcurementAuthorizationDenied,
            psycopg.Error,
            SQLAlchemyError,
        ) as error:
            return procurement_problem(error, correlation_id)

    @router.post(
        "/offers",
        response_model=SupplierOfferResponse,
        status_code=201,
        operation_id="createProcurementSupplierOffer",
        summary="Create an effective-dated supplier offer",
        responses=PROCUREMENT_RESPONSES,
    )
    def create_offer(
        request: SupplierOfferRequest,
        gl_session: str | None = Security(session_cookie),
    ):
        correlation_id = str(uuid4())
        try:
            return offer_response(
                service.create_supplier_offer(
                    procurement_identity(gl_session),
                    CreateSupplierOffer(
                        supplier_id=request.supplierId,
                        ingredient_id=request.ingredientId,
                        purchase_unit_id=request.purchaseUnitId,
                        price=request.price,
                        currency=request.currency,
                        effective_from=request.effectiveFrom,
                        effective_until=request.effectiveUntil,
                    ),
                    correlation_id=correlation_id,
                )
            )
        except (
            AuthenticationRequired,
            ProcurementAuthorizationDenied,
            ProcurementValidationError,
            ProcurementNotFound,
            ProcurementUnitMismatch,
            ProcurementDateOverlap,
            ProcurementCodeConflict,
            psycopg.Error,
            SQLAlchemyError,
        ) as error:
            return procurement_problem(error, correlation_id)

    @router.post(
        "/supplier-receipts/{receiptId}/accept",
        response_model=SupplierReceiptResponse,
        status_code=201,
        operation_id="acceptSupplierReceipt",
        summary="Accept a supplier receipt into the immutable inventory ledger",
        responses=PROCUREMENT_RESPONSES,
    )
    def accept_supplier_receipt(
        receiptId: str,
        request: SupplierReceiptRequest,
        gl_session: str | None = Security(session_cookie),
    ):
        correlation_id = str(uuid4())
        try:
            return receipt_response(
                receipts.accept_supplier_receipt(
                    procurement_identity(gl_session),
                    CreateSupplierReceipt(
                        idempotency_key=receiptId,
                        order_reference=request.orderReference,
                        supplier_id=request.supplierId,
                        warehouse_id=request.warehouseId,
                        received_on=request.receivedOn,
                        lines=tuple(
                            CreateSupplierReceiptLine(
                                ingredient_id=line.ingredientId,
                                purchase_unit_id=line.purchaseUnitId,
                                lot_code=line.lotCode,
                                ordered_quantity=line.orderedQuantity,
                                delivered_quantity=line.deliveredQuantity,
                                unit_cost=line.unitCost,
                                expiry_date=line.expiryDate,
                                temperature=line.temperature,
                                minimum_temperature=line.minimumTemperature,
                                maximum_temperature=line.maximumTemperature,
                                tolerance_percent=line.tolerancePercent,
                            )
                            for line in request.lines
                        ),
                    ),
                    correlation_id=correlation_id,
                )
            )
        except (
            AuthenticationRequired,
            ProcurementAuthorizationDenied,
            ProcurementValidationError,
            ProcurementNotFound,
            ProcurementUnitMismatch,
            ProcurementCodeConflict,
            psycopg.Error,
            SQLAlchemyError,
        ) as error:
            return procurement_problem(error, correlation_id)

    return router
