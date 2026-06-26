from dataclasses import dataclass

from gastroledger_api.application.identifiers import BranchId, TenantId

MODULE_ID = "control_insights"


@dataclass(frozen=True)
class OrderingHoldDecision:
    tenant_id: TenantId
    branch_id: BranchId
    blocked: bool
    reason_code: str | None = None


@dataclass(frozen=True)
class ProjectionRequest:
    tenant_id: TenantId
    projection_type: str
    source_reference: str


@dataclass(frozen=True)
class ProjectionReference:
    tenant_id: TenantId
    projection_id: str

