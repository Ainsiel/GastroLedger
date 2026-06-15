const endpoints = [
  ["api", process.env.API_HEALTH_URL ?? "http://127.0.0.1:58000/health"],
  ["web", process.env.WEB_HEALTH_URL ?? "http://127.0.0.1:53000/api/health"],
];

for (const [service, url] of endpoints) {
  const response = await fetch(url);
  const body = await response.json();

  if (!response.ok || body.service !== service || body.status !== "ok") {
    throw new Error(`${service} critical smoke check failed`);
  }
}

console.log("Critical technical smoke checks passed.");

const webBaseUrl = new URL(
  process.env.WEB_HEALTH_URL ?? "http://127.0.0.1:53000/api/health",
).origin;
const slug = `e2e-${Date.now()}`;
const registration = await fetch(`${webBaseUrl}/api/v1/tenants/register`, {
  method: "POST",
  headers: { "content-type": "application/json" },
  body: JSON.stringify({
    tenantName: "E2E Tenant",
    tenantSlug: slug,
    adminEmail: `${slug}@example.com`,
    password: "StrongPassword123",
  }),
});
const registrationBody = await registration.json();
const cookie = registration.headers.get("set-cookie");

if (!registration.ok || registrationBody.tenantSlug !== slug || !cookie) {
  throw new Error("tenant registration critical smoke check failed");
}

const identity = await fetch(`${webBaseUrl}/api/v1/session/tenant`, {
  headers: { cookie },
});
const identityBody = await identity.json();

if (!identity.ok || identityBody.tenantId !== registrationBody.tenantId) {
  throw new Error("scoped tenant identity critical smoke check failed");
}

console.log("Critical tenant registration smoke checks passed.");

const settings = await fetch(`${webBaseUrl}/api/v1/tenant/settings`, {
  method: "PATCH",
  headers: { "content-type": "application/json", cookie },
  body: JSON.stringify({ locale: "es", baseCurrency: "CLP", branchLimit: 2 }),
});
const settingsBody = await settings.json();
if (!settings.ok || settingsBody.baseCurrency !== "CLP") {
  throw new Error("tenant settings critical smoke check failed");
}

const branch = await fetch(`${webBaseUrl}/api/v1/branches`, {
  method: "POST",
  headers: { "content-type": "application/json", cookie },
  body: JSON.stringify({ name: "Downtown", code: "MAIN" }),
});
const branchBody = await branch.json();
if (!branch.ok || branchBody.code !== "MAIN") {
  throw new Error("branch creation critical smoke check failed");
}

const warehouse = await fetch(
  `${webBaseUrl}/api/v1/branches/${branchBody.branchId}/warehouses`,
  {
    method: "POST",
    headers: { "content-type": "application/json", cookie },
    body: JSON.stringify({ name: "Main kitchen", code: "KITCHEN", type: "kitchen" }),
  },
);
const warehouseBody = await warehouse.json();
if (!warehouse.ok || warehouseBody.status !== "active") {
  throw new Error("warehouse creation critical smoke check failed");
}

const settingsRoute = await fetch(`${webBaseUrl}/settings`, { headers: { cookie } });
const settingsRouteBody = await settingsRoute.text();
if (
  !settingsRoute.ok ||
  !settingsRouteBody.includes("Organization settings") ||
  !settingsRouteBody.includes("Downtown") ||
  !settingsRouteBody.includes("Main kitchen")
) {
  throw new Error("integrated operating scope route critical smoke check failed");
}

const deactivated = await fetch(
  `${webBaseUrl}/api/v1/warehouses/${warehouseBody.warehouseId}/deactivate`,
  { method: "POST", headers: { cookie } },
);
const deactivatedBody = await deactivated.json();
if (!deactivated.ok || deactivatedBody.status !== "inactive") {
  throw new Error("warehouse deactivation critical smoke check failed");
}

console.log("Critical tenant operating scope smoke checks passed.");
