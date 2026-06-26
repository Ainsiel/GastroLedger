from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime

from gastroledger_api.application.identifiers import (
    ActorId,
    CorrelationId,
    EventId,
    JobId,
    TenantId,
)


@dataclass(frozen=True)
class AuditRecord:
    tenant_id: TenantId
    actor_id: ActorId
    correlation_id: CorrelationId
    action: str
    object_reference: str
    occurred_at: datetime


@dataclass(frozen=True)
class JobRequest:
    job_id: JobId
    tenant_id: TenantId
    job_type: str
    payload: Mapping[str, object]


@dataclass(frozen=True)
class OutboxEvent:
    event_id: EventId
    tenant_id: TenantId
    event_type: str
    payload: Mapping[str, object]
    occurred_at: datetime
