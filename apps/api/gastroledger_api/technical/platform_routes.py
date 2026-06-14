import os
from uuid import uuid4

import psycopg
from fastapi import APIRouter, Cookie, Query, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from gastroledger_api.modules.platform_organization.application.registration import (
    RegisterTenant,
    RegistrationCommand,
    RegistrationConflict,
)
from gastroledger_api.modules.platform_organization.application.security import (
    ScryptPasswordHasher,
    SessionTokenIssuer,
)
from gastroledger_api.modules.platform_organization.domain.registration import (
    RegistrationValidationError,
)
from gastroledger_api.technical.postgres_platform import PostgresPlatformStore

SESSION_COOKIE = "gl_session"


class FirstBranchRequest(BaseModel):
    name: str
    code: str


class RegistrationRequest(BaseModel):
    tenantName: str
    tenantSlug: str
    adminEmail: str
    password: str
    firstBranch: FirstBranchRequest | None = None


class RegistrationResponse(BaseModel):
    tenantId: str
    actorId: str
    branchId: str | None
    tenantName: str
    tenantSlug: str


class TenantIdentityResponse(BaseModel):
    tenantId: str
    actorId: str
    tenantName: str
    tenantSlug: str


def problem(status: int, code: str, correlation_id: str, errors: list[dict[str, str]]):
    return JSONResponse(
        status_code=status,
        content={
            "type": code,
            "title": "The request could not be completed",
            "status": status,
            "correlationId": correlation_id,
            "errors": errors,
        },
    )


def create_platform_router(database_url: str | None = None) -> APIRouter:
    router = APIRouter(prefix="/api/v1", tags=["platform-organization"])
    store = PostgresPlatformStore(database_url or os.environ.get("DATABASE_URL", ""))
    register_tenant = RegisterTenant(
        store=store,
        password_hasher=ScryptPasswordHasher(),
        session_tokens=SessionTokenIssuer(),
    )

    @router.post("/tenants/register", response_model=RegistrationResponse, status_code=201)
    def register(request: RegistrationRequest, response: Response):
        correlation_id = str(uuid4())
        try:
            result = register_tenant.execute(
                RegistrationCommand(
                    tenant_name=request.tenantName,
                    tenant_slug=request.tenantSlug,
                    admin_email=request.adminEmail,
                    password=request.password,
                    branch_name=request.firstBranch.name if request.firstBranch else None,
                    branch_code=request.firstBranch.code if request.firstBranch else None,
                )
            )
        except RegistrationValidationError as error:
            return problem(
                422,
                "platform.registration_invalid",
                correlation_id,
                [
                    {"field": detail.field, "code": detail.code, "detail": "review field"}
                    for detail in error.details
                ],
            )
        except RegistrationConflict:
            return problem(
                409,
                "platform.tenant_slug_conflict",
                correlation_id,
                [{"field": "tenantSlug", "code": "duplicate", "detail": "already registered"}],
            )
        except psycopg.Error:
            return problem(500, "platform.registration_failed", correlation_id, [])
        response.set_cookie(
            key=SESSION_COOKIE,
            value=result.session_token,
            max_age=8 * 60 * 60,
            httponly=True,
            secure=os.environ.get("GL_ENVIRONMENT") not in {"development", "integration"},
            samesite="strict",
            path="/",
        )
        return RegistrationResponse(
            tenantId=str(result.tenant_id),
            actorId=str(result.actor_id),
            branchId=str(result.branch_id) if result.branch_id else None,
            tenantName=result.tenant_name,
            tenantSlug=result.tenant_slug,
        )

    @router.get("/session/tenant", response_model=TenantIdentityResponse)
    def tenant_identity(
        tenantId: str | None = Query(default=None),
        gl_session: str | None = Cookie(default=None),
    ):
        correlation_id = str(uuid4())
        if not gl_session:
            return problem(401, "platform.authentication_required", correlation_id, [])
        try:
            identity = store.resolve_tenant(gl_session, tenantId, correlation_id)
        except psycopg.Error:
            return problem(500, "platform.tenant_identity_failed", correlation_id, [])
        if not identity:
            return problem(404, "platform.tenant_not_found", correlation_id, [])
        return TenantIdentityResponse(
            tenantId=str(identity.tenant_id),
            actorId=str(identity.actor_id),
            tenantName=identity.tenant_name,
            tenantSlug=identity.tenant_slug,
        )

    return router
