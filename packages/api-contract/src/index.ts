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

export type UserRole = "branch_manager" | "branch_operator" | "tenant_operator";
export type UserRoleScope = "branch" | "tenant";

export interface InvitationRequest {
  inviteeLogin: string;
  role: UserRole;
  scope: UserRoleScope;
  branchId?: string | null;
  ttlHours: number;
}

export interface InvitationResponse extends InvitationRequest {
  invitationId: string;
  manualShareToken: string;
  expiresAt: string;
  status: "pending";
}

export interface InvitationAcceptanceRequest {
  manualShareToken: string;
  password: string;
}

export interface InvitationAcceptanceResponse extends TenantIdentityResponse {}

export interface BranchAccessResponse {
  branchIds: string[];
}

export type UnitDimension = "mass" | "volume" | "count";

export interface UnitRequest {
  name: string;
  code: string;
  dimension: UnitDimension;
}

export interface ConversionFactorRequest {
  sourceUnitId: string;
  targetUnitId: string;
  factor: string;
  effectiveFrom: string;
}

export interface ConversionFactorResponse extends ConversionFactorRequest {
  conversionFactorId: string;
}

export interface UnitResponse extends UnitRequest {
  unitId: string;
  conversions: ConversionFactorResponse[];
}

export interface IngredientRequest {
  name: string;
  code: string;
  purchaseUnitId: string;
  consumptionUnitId: string;
  shelfLifeDays: number;
  criticalStockQuantity: string;
}

export interface IngredientResponse extends IngredientRequest {
  ingredientId: string;
  status: "active" | "archived";
  availableForNewUse: boolean;
}

export type RecipeComponentType = "ingredient" | "sub_recipe";

export interface RecipeComponentRequest {
  componentType: RecipeComponentType;
  componentId: string;
  quantity: string;
  unitId: string;
}

export interface SubRecipeVersionRequest {
  name: string;
  code: string;
  version: string;
  yieldQuantity: string;
  yieldUnitId: string;
  effectiveFrom: string;
  components: RecipeComponentRequest[];
}

export interface MenuItemVersionRequest extends SubRecipeVersionRequest {}

export interface BranchMenuPriceRequest {
  branchId: string;
  price: string;
  currency: string;
  effectiveFrom: string;
}

export interface RecipeComponentResponse extends RecipeComponentRequest {}

export interface CostSnapshotResponse {
  totalCost: string;
  status: "current" | "missing_cost";
}

export interface CostProjectionResponse {
  status: "current" | "pending" | "stale" | "failed";
  updatedAt: string;
  lastError?: string | null;
}

export interface SubRecipeVersionResponse extends SubRecipeVersionRequest {
  recipeId: string;
  recipeVersionId: string;
  status: "approved" | "scheduled";
  isActive: boolean;
  costSnapshot: CostSnapshotResponse;
  costProjection?: CostProjectionResponse;
  components: RecipeComponentResponse[];
}

export interface BranchMenuMarginResponse extends BranchMenuPriceRequest {
  branchPriceId: string;
  menuItemVersionId: string;
  theoreticalCost: string;
  contributionMargin: string;
  marginPercent: string;
  suggestedPrice: string;
}

export interface MenuItemVersionResponse extends MenuItemVersionRequest {
  recipeId: string;
  recipeVersionId: string;
  status: "approved" | "scheduled";
  isActive: boolean;
  costSnapshot: CostSnapshotResponse;
  costProjection?: CostProjectionResponse;
  components: RecipeComponentResponse[];
  branchMargins: BranchMenuMarginResponse[];
}

export interface SupplierRequest {
  name: string;
  code: string;
}

export interface SupplierResponse extends SupplierRequest {
  supplierId: string;
  status: "active" | "inactive";
}

export interface SupplierOfferRequest {
  supplierId: string;
  ingredientId: string;
  purchaseUnitId: string;
  price: string;
  currency: string;
  effectiveFrom: string;
  effectiveUntil?: string | null;
}

export interface SupplierOfferResponse extends SupplierOfferRequest {
  supplierOfferId: string;
}

export interface ApiProblem {
  type: string;
  title: string;
  status: number;
  correlationId: string;
  errors: Array<{ field?: string; code: string; detail: string }>;
}

