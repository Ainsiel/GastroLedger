from collections.abc import Iterable
from contextlib import AbstractAsyncContextManager
from datetime import datetime
from typing import BinaryIO, Protocol

from gastroledger_api.application.messages import AuditRecord, JobRequest, OutboxEvent
from gastroledger_api.application.security import (
    AuthorizationDecision,
    AuthorizationRequest,
    TenantContext,
)
from gastroledger_api.modules.control_insights.public import (
    ProjectionReference,
    ProjectionRequest,
)
from gastroledger_api.modules.inventory_production.public import (
    AllocationOutcome,
    AllocationRequest,
    InventoryPosting,
    InventoryTransactionReference,
)
from gastroledger_api.modules.menu_engineering.public import (
    ApprovedRecipeVersionReference,
    ApprovedRecipeVersionSnapshot,
    UnitConversionRequest,
    UnitConversionResult,
)
from gastroledger_api.modules.store_operations.public import ImportRow


class TenantContextProvider(Protocol):
    def current(self) -> TenantContext: ...


class AuthorizationPolicy(Protocol):
    async def decide(self, request: AuthorizationRequest) -> AuthorizationDecision: ...


class TransactionManager(Protocol):
    def transaction(self, context: TenantContext) -> AbstractAsyncContextManager[None]: ...


class AuditSink(Protocol):
    async def append(self, record: AuditRecord) -> None: ...


class JobQueue(Protocol):
    async def enqueue(self, request: JobRequest) -> None: ...


class EventOutbox(Protocol):
    async def append(self, event: OutboxEvent) -> None: ...


class Clock(Protocol):
    def now(self) -> datetime: ...


class RecipeCatalog(Protocol):
    async def resolve_approved(
        self, reference: ApprovedRecipeVersionReference
    ) -> ApprovedRecipeVersionSnapshot: ...


class UnitConversionPolicy(Protocol):
    def convert(self, request: UnitConversionRequest) -> UnitConversionResult: ...


class InventoryLedger(Protocol):
    async def post(self, posting: InventoryPosting) -> InventoryTransactionReference: ...


class LotAllocator(Protocol):
    async def allocate(self, request: AllocationRequest) -> AllocationOutcome: ...


class CostProjection(Protocol):
    async def request(self, request: ProjectionRequest) -> ProjectionReference: ...


class ImportReader(Protocol):
    def rows(self, source: BinaryIO) -> Iterable[ImportRow]: ...
