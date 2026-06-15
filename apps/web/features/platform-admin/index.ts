export const featureId = "platform-admin" as const;

export { DashboardPage } from "./dashboard-page";
export { OperatingScopePage } from "./operating-scope-page";
export { loadOperatingScope, operatingRequest } from "./operating-scope";
export type { OperatingOutcome, OperatingScopeSnapshot } from "./operating-scope";
