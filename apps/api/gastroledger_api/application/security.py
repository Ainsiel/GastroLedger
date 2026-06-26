from dataclasses import dataclass

from gastroledger_api.application.identifiers import ActorId, BranchId, TenantId


@dataclass(frozen=True)
class TenantContext:
    tenant_id: TenantId
    actor_id: ActorId
    branch_scope: frozenset[BranchId] = frozenset()


@dataclass(frozen=True)
class AuthorizationRequest:
    context: TenantContext
    capability: str
    branch_id: BranchId | None = None


@dataclass(frozen=True)
class AuthorizationDecision:
    allowed: bool
    reason_code: str | None = None

