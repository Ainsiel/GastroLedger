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

export interface ApiProblem {
  type: string;
  title: string;
  status: number;
  correlationId: string;
  errors: Array<{ field?: string; code: string; detail: string }>;
}

