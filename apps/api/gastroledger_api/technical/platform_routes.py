import os
from uuid import UUID, uuid4

import psycopg
from fastapi import APIRouter, Query, Response, Security
from fastapi.security import APIKeyCookie
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.exc import SQLAlchemyError

from gastroledger_api.modules.platform_organization.public import (
    AuthenticationRequired,
    BranchId,
    BranchLimitExceeded,
    BranchView,
    CreateBranch,
    CreateWarehouse,
    DeactivateWarehouse,
    InvalidCredentials,
    OperatingAuthorizationDenied,
    OperatingCodeConflict,
    OperatingIdentity,
    OperatingNotFound,
    OperatingScopeService,
    OperatingValidationError,
    RegisterTenant,
    RegistrationCommand,
    RegistrationConflict,
    RegistrationValidationError,
    ScryptPasswordHasher,
    SessionTokenIssuer,
    TenantLoginAmbiguous,
    TenantSettingsView,
    UpdateTenantSettings,
    WarehouseDeactivationUnsafe,
    WarehouseId,
    WarehouseInactive,
    WarehouseMovementGuard,
    WarehouseView,
)
from gastroledger_api.technical.postgres_platform import PostgresPlatformStore
from gastroledger_api.technical.problems import ApiProblem, problem_response

SESSION_COOKIE = "gl_session"
session_cookie = APIKeyCookie(
    name=SESSION_COOKIE,
    auto_error=False,
    description="Opaque local session cookie issued after tenant registration or login.",
)

REGISTRATION_RESPONSES = {
    409: {"model": ApiProblem, "description": "The tenant identifier already exists."},
    422: {"model": ApiProblem, "description": "The bounded registration input is invalid."},
    429: {"model": ApiProblem, "description": "The public registration limit was reached."},
    500: {"model": ApiProblem, "description": "Registration could not be completed."},
}

TENANT_IDENTITY_RESPONSES = {
    401: {"model": ApiProblem, "description": "A valid local session is required."},
    404: {"model": ApiProblem, "description": "The scoped tenant is not visible."},
    422: {"model": ApiProblem, "description": "The query parameter is invalid."},
    500: {"model": ApiProblem, "description": "Tenant identity could not be resolved."},
}

SESSION_LOGIN_RESPONSES = {
    401: {"model": ApiProblem, "description": "The credentials are invalid."},
    409: {"model": ApiProblem, "description": "The login belongs to multiple tenants."},
    422: {"model": ApiProblem, "description": "The bounded login input is invalid."},
    500: {"model": ApiProblem, "description": "Login could not be completed."},
}

SESSION_LOGOUT_RESPONSES = {
    500: {"model": ApiProblem, "description": "Logout could not be completed."},
}

OPERATING_RESPONSES = {
    401: {"model": ApiProblem, "description": "A valid local session is required."},
    403: {"model": ApiProblem, "description": "Tenant administrator access is required."},
    404: {"model": ApiProblem, "description": "The scoped resource is not visible."},
    409: {"model": ApiProblem, "description": "The operating-scope command conflicts."},
    422: {"model": ApiProblem, "description": "The operating-scope input is invalid."},
    500: {"model": ApiProblem, "description": "The command could not be completed."},
}


class FirstBranchRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=120)
    code: str = Field(min_length=1, max_length=63)


class RegistrationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tenantName: str = Field(min_length=1, max_length=120)
    tenantSlug: str = Field(min_length=1, max_length=63)
    adminEmail: str = Field(min_length=1, max_length=254)
    password: str = Field(min_length=1, max_length=128)
    firstBranch: FirstBranchRequest | None = None


class RegistrationResponse(BaseModel):
    tenantId: str
    actorId: str
    branchId: str | None
    tenantName: str
    tenantSlug: str


class LoginRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: str = Field(min_length=1, max_length=254)
    password: str = Field(min_length=1, max_length=128)


class TenantIdentityResponse(BaseModel):
    tenantId: str
    actorId: str
    tenantName: str
    tenantSlug: str


class TenantSettingsRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    locale: str = Field(min_length=1, max_length=20)
    baseCurrency: str = Field(min_length=3, max_length=3)
    branchLimit: int = Field(strict=True, ge=1, le=100)


class TenantSettingsResponse(BaseModel):
    locale: str
    baseCurrency: str
    branchLimit: int
    branchCount: int


class BranchRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=120)
    code: str = Field(min_length=1, max_length=63)


class WarehouseRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=120)
    code: str = Field(min_length=1, max_length=63)
    type: str = Field(min_length=1, max_length=20)


class WarehouseResponse(BaseModel):
    warehouseId: str
    branchId: str
    name: str
    code: str
    type: str
    status: str


class BranchResponse(BaseModel):
    branchId: str
    name: str
    code: str
    warehouses: list[WarehouseResponse]


class NoOpenWarehouseMovements(WarehouseMovementGuard):
    def has_open_movements(
        self, _identity: OperatingIdentity, _warehouse_id: WarehouseId
    ) -> bool:
        # Inventory movement lifecycles are introduced by later accepted slices.
        return False


def settings_response(settings: TenantSettingsView) -> TenantSettingsResponse:
    return TenantSettingsResponse(
        locale=settings.locale,
        baseCurrency=settings.base_currency,
        branchLimit=settings.branch_limit,
        branchCount=settings.branch_count,
    )


def warehouse_response(warehouse: WarehouseView) -> WarehouseResponse:
    return WarehouseResponse(
        warehouseId=str(warehouse.warehouse_id),
        branchId=str(warehouse.branch_id),
        name=warehouse.name,
        code=warehouse.code,
        type=warehouse.warehouse_type,
        status=warehouse.status,
    )


def branch_response(branch: BranchView) -> BranchResponse:
    return BranchResponse(
        branchId=str(branch.branch_id),
        name=branch.name,
        code=branch.code,
        warehouses=[warehouse_response(item) for item in branch.warehouses],
    )


def create_platform_router(database_url: str | None = None) -> APIRouter:
    router = APIRouter(prefix="/api/v1", tags=["platform-organization"])
    store = PostgresPlatformStore(database_url or os.environ.get("DATABASE_URL", ""))
    password_hasher = ScryptPasswordHasher()
    session_tokens = SessionTokenIssuer()
    register_tenant = RegisterTenant(
        store=store,
        password_hasher=password_hasher,
        session_tokens=session_tokens,
    )
    operating_scope = OperatingScopeService(
        store=store, movement_guard=NoOpenWarehouseMovements()
    )

    def operating_identity(gl_session: str | None) -> OperatingIdentity:
        if not gl_session:
            raise AuthenticationRequired
        return store.resolve_operating_identity(gl_session)

    def set_session_cookie(response: Response, token: str) -> None:
        response.set_cookie(
            key=SESSION_COOKIE,
            value=token,
            max_age=8 * 60 * 60,
            httponly=True,
            secure=os.environ.get("GL_ENVIRONMENT") not in {"development", "integration"},
            samesite="strict",
            path="/",
        )

    def operating_problem(error: Exception, correlation_id: str):
        if isinstance(error, AuthenticationRequired):
            return problem_response(
                401, "platform.authentication_required", correlation_id, []
            )
        if isinstance(error, OperatingAuthorizationDenied):
            return problem_response(403, "platform.authorization_denied", correlation_id, [])
        if isinstance(error, OperatingNotFound):
            return problem_response(404, "platform.operating_scope_not_found", correlation_id, [])
        if isinstance(error, OperatingValidationError):
            return problem_response(
                422,
                "platform.operating_scope_invalid",
                correlation_id,
                [
                    {"field": detail.field, "code": detail.code, "detail": "review field"}
                    for detail in error.details
                ],
            )
        if isinstance(error, OperatingCodeConflict):
            return problem_response(409, "platform.code_conflict", correlation_id, [])
        if isinstance(error, BranchLimitExceeded):
            return problem_response(
                409,
                "platform.branch_limit_exceeded",
                correlation_id,
                [{"field": "branchLimit", "code": "exceeded", "detail": "review limit"}],
            )
        if isinstance(error, WarehouseInactive):
            return problem_response(409, "platform.warehouse_inactive", correlation_id, [])
        if isinstance(error, WarehouseDeactivationUnsafe):
            return problem_response(
                409, "platform.warehouse_has_open_movements", correlation_id, []
            )
        return problem_response(500, "platform.operating_scope_failed", correlation_id, [])

    @router.post(
        "/tenants/register",
        response_model=RegistrationResponse,
        status_code=201,
        operation_id="registerTenant",
        summary="Register a tenant and first administrator",
        description=(
            "Atomically creates an isolated local tenant, its first administrator, "
            "an optional first branch and a scoped local session."
        ),
        responses=REGISTRATION_RESPONSES,
    )
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
            return problem_response(
                422,
                "platform.registration_invalid",
                correlation_id,
                [
                    {"field": detail.field, "code": detail.code, "detail": "review field"}
                    for detail in error.details
                ],
            )
        except RegistrationConflict:
            return problem_response(
                409,
                "platform.tenant_slug_conflict",
                correlation_id,
                [{"field": "tenantSlug", "code": "duplicate", "detail": "already registered"}],
            )
        except (psycopg.Error, SQLAlchemyError):
            return problem_response(500, "platform.registration_failed", correlation_id, [])
        set_session_cookie(response, result.session_token)
        return RegistrationResponse(
            tenantId=str(result.tenant_id),
            actorId=str(result.actor_id),
            branchId=str(result.branch_id) if result.branch_id else None,
            tenantName=result.tenant_name,
            tenantSlug=result.tenant_slug,
        )

    @router.post(
        "/session/login",
        response_model=TenantIdentityResponse,
        operation_id="loginSession",
        summary="Start a tenant-scoped local session",
        description=(
            "Authenticates a local user by email and password. If that login belongs "
            "to exactly one active tenant, a scoped gl_session cookie is issued."
        ),
        responses=SESSION_LOGIN_RESPONSES,
    )
    def login(request: LoginRequest, response: Response):
        correlation_id = str(uuid4())
        try:
            result = store.login(
                request.email,
                request.password,
                password_hasher,
                session_tokens,
            )
        except InvalidCredentials:
            return problem_response(401, "platform.invalid_credentials", correlation_id, [])
        except TenantLoginAmbiguous:
            return problem_response(
                409,
                "platform.login_tenant_ambiguous",
                correlation_id,
                [{"field": "email", "code": "tenant_ambiguous", "detail": "select tenant"}],
            )
        except (psycopg.Error, SQLAlchemyError):
            return problem_response(500, "platform.login_failed", correlation_id, [])
        set_session_cookie(response, result.session_token)
        return TenantIdentityResponse(
            tenantId=str(result.tenant_id),
            actorId=str(result.actor_id),
            tenantName=result.tenant_name,
            tenantSlug=result.tenant_slug,
        )

    @router.post(
        "/session/logout",
        status_code=204,
        operation_id="logoutSession",
        summary="End the current local session",
        responses=SESSION_LOGOUT_RESPONSES,
    )
    def logout(response: Response, gl_session: str | None = Security(session_cookie)):
        correlation_id = str(uuid4())
        try:
            if gl_session:
                store.revoke_session(gl_session)
        except (psycopg.Error, SQLAlchemyError):
            return problem_response(500, "platform.logout_failed", correlation_id, [])
        response.delete_cookie(key=SESSION_COOKIE, path="/", samesite="strict")
        return None

    @router.get(
        "/session/tenant",
        response_model=TenantIdentityResponse,
        operation_id="getCurrentTenant",
        summary="Resolve the tenant for the current local session",
        responses=TENANT_IDENTITY_RESPONSES,
    )
    def tenant_identity(
        tenantId: UUID | None = Query(default=None),
        gl_session: str | None = Security(session_cookie),
    ):
        correlation_id = str(uuid4())
        if not gl_session:
            return problem_response(401, "platform.authentication_required", correlation_id, [])
        try:
            identity = store.resolve_tenant(
                gl_session, str(tenantId) if tenantId else None, correlation_id
            )
        except AuthenticationRequired:
            return problem_response(
                401, "platform.authentication_required", correlation_id, []
            )
        except (psycopg.Error, SQLAlchemyError):
            return problem_response(500, "platform.tenant_identity_failed", correlation_id, [])
        if not identity:
            return problem_response(404, "platform.tenant_not_found", correlation_id, [])
        return TenantIdentityResponse(
            tenantId=str(identity.tenant_id),
            actorId=str(identity.actor_id),
            tenantName=identity.tenant_name,
            tenantSlug=identity.tenant_slug,
        )

    @router.get(
        "/tenant/settings",
        response_model=TenantSettingsResponse,
        operation_id="getTenantSettings",
        summary="Get tenant operating settings",
        responses=OPERATING_RESPONSES,
    )
    def get_tenant_settings(gl_session: str | None = Security(session_cookie)):
        correlation_id = str(uuid4())
        try:
            return settings_response(
                operating_scope.get_settings(operating_identity(gl_session))
            )
        except (
            AuthenticationRequired,
            OperatingAuthorizationDenied,
            psycopg.Error,
            SQLAlchemyError,
        ) as error:
            return operating_problem(error, correlation_id)

    @router.patch(
        "/tenant/settings",
        response_model=TenantSettingsResponse,
        operation_id="updateTenantSettings",
        summary="Update tenant operating settings",
        responses=OPERATING_RESPONSES,
    )
    def update_tenant_settings(
        request: TenantSettingsRequest,
        gl_session: str | None = Security(session_cookie),
    ):
        correlation_id = str(uuid4())
        try:
            return settings_response(
                operating_scope.update_settings(
                    operating_identity(gl_session),
                    UpdateTenantSettings(
                        locale=request.locale,
                        base_currency=request.baseCurrency,
                        branch_limit=request.branchLimit,
                    ),
                    correlation_id=correlation_id,
                )
            )
        except (
            AuthenticationRequired,
            OperatingAuthorizationDenied,
            OperatingValidationError,
            psycopg.Error,
            SQLAlchemyError,
        ) as error:
            return operating_problem(error, correlation_id)

    @router.get(
        "/branches",
        response_model=list[BranchResponse],
        operation_id="listBranches",
        summary="List tenant branches and warehouses",
        responses=OPERATING_RESPONSES,
    )
    def list_branches(gl_session: str | None = Security(session_cookie)):
        correlation_id = str(uuid4())
        try:
            return [
                branch_response(branch)
                for branch in operating_scope.list_branches(
                    operating_identity(gl_session)
                )
            ]
        except (
            AuthenticationRequired,
            OperatingAuthorizationDenied,
            psycopg.Error,
            SQLAlchemyError,
        ) as error:
            return operating_problem(error, correlation_id)

    @router.post(
        "/branches",
        response_model=BranchResponse,
        status_code=201,
        operation_id="createBranch",
        summary="Create a tenant branch",
        responses=OPERATING_RESPONSES,
    )
    def create_branch(
        request: BranchRequest,
        gl_session: str | None = Security(session_cookie),
    ):
        correlation_id = str(uuid4())
        try:
            return branch_response(
                operating_scope.create_branch(
                    operating_identity(gl_session),
                    CreateBranch(name=request.name, code=request.code),
                    correlation_id=correlation_id,
                )
            )
        except (
            AuthenticationRequired,
            OperatingAuthorizationDenied,
            OperatingValidationError,
            OperatingCodeConflict,
            BranchLimitExceeded,
            psycopg.Error,
            SQLAlchemyError,
        ) as error:
            return operating_problem(error, correlation_id)

    @router.post(
        "/branches/{branchId}/warehouses",
        response_model=WarehouseResponse,
        status_code=201,
        operation_id="createWarehouse",
        summary="Create a branch warehouse",
        responses=OPERATING_RESPONSES,
    )
    def create_warehouse(
        branchId: UUID,
        request: WarehouseRequest,
        gl_session: str | None = Security(session_cookie),
    ):
        correlation_id = str(uuid4())
        try:
            return warehouse_response(
                operating_scope.create_warehouse(
                    operating_identity(gl_session),
                    CreateWarehouse(
                        branch_id=BranchId(str(branchId)),
                        name=request.name,
                        code=request.code,
                        warehouse_type=request.type,
                    ),
                    correlation_id=correlation_id,
                )
            )
        except (
            AuthenticationRequired,
            OperatingAuthorizationDenied,
            OperatingValidationError,
            OperatingCodeConflict,
            OperatingNotFound,
            psycopg.Error,
            SQLAlchemyError,
        ) as error:
            return operating_problem(error, correlation_id)

    @router.post(
        "/warehouses/{warehouseId}/deactivate",
        response_model=WarehouseResponse,
        operation_id="deactivateWarehouse",
        summary="Deactivate an unused warehouse",
        responses=OPERATING_RESPONSES,
    )
    def deactivate_warehouse(
        warehouseId: UUID,
        gl_session: str | None = Security(session_cookie),
    ):
        correlation_id = str(uuid4())
        try:
            return warehouse_response(
                operating_scope.deactivate_warehouse(
                    operating_identity(gl_session),
                    DeactivateWarehouse(warehouse_id=WarehouseId(str(warehouseId))),
                    correlation_id=correlation_id,
                )
            )
        except (
            AuthenticationRequired,
            OperatingAuthorizationDenied,
            OperatingNotFound,
            WarehouseDeactivationUnsafe,
            WarehouseInactive,
            psycopg.Error,
            SQLAlchemyError,
        ) as error:
            return operating_problem(error, correlation_id)

    return router
