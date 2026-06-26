from dataclasses import dataclass

from gastroledger_api.application.identifiers import CorrelationId
from gastroledger_api.application.security import TenantContext


@dataclass(frozen=True)
class RequestEnvelope[InputT]:
    payload: InputT
    context: TenantContext
    correlation_id: CorrelationId


@dataclass(frozen=True)
class ApplicationResult[OutputT]:
    value: OutputT
    correlation_id: CorrelationId
