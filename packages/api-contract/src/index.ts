export type HealthService = "web" | "api" | "worker";

export interface HealthResponse {
  service: HealthService;
  status: "ok";
}

export interface FirstBranchRegistration {
  name: string;
  code: string;
}

export interface TenantRegistrationRequest {
  tenantName: string;
  tenantSlug: string;
  adminEmail: string;
  password: string;
  firstBranch?: FirstBranchRegistration;
}

export interface TenantRegistrationResponse {
  tenantId: string;
  actorId: string;
  branchId: string | null;
  tenantName: string;
  tenantSlug: string;
}

export interface TenantIdentityResponse {
  tenantId: string;
  actorId: string;
  tenantName: string;
  tenantSlug: string;
}

export interface SessionLoginRequest {
  email: string;
  password: string;
}

export type SessionLoginResponse = TenantIdentityResponse;

export interface TenantSettingsRequest {
  locale: string;
  baseCurrency: string;
  branchLimit: number;
}

export interface TenantSettingsResponse extends TenantSettingsRequest {
  branchCount: number;
}

export interface BranchRequest {
  name: string;
  code: string;
}

export interface WarehouseRequest {
  name: string;
  code: string;
  type: "kitchen" | "bar" | "general";
}

export interface WarehouseResponse extends WarehouseRequest {
  warehouseId: string;
  branchId: string;
  status: "active" | "inactive";
}

export interface BranchResponse extends BranchRequest {
  branchId: string;
  warehouses: WarehouseResponse[];
}

export interface ApiProblem {
  type: string;
  title: string;
  status: number;
  correlationId: string;
  errors: Array<{ field?: string; code: string; detail: string }>;
}

