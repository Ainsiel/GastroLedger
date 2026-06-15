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
