const apiBaseUrl = process.env.API_BASE_URL ?? "http://api:8000";

export async function GET(request: Request) {
  const url = new URL(request.url);
  const upstreamUrl = new URL("/api/v1/session/tenant", apiBaseUrl);
  const tenantId = url.searchParams.get("tenantId");
  if (tenantId) {
    upstreamUrl.searchParams.set("tenantId", tenantId);
  }
  const upstream = await fetch(upstreamUrl, {
    headers: { cookie: request.headers.get("cookie") ?? "" },
    cache: "no-store",
  });
  return new Response(await upstream.text(), {
    status: upstream.status,
    headers: { "content-type": upstream.headers.get("content-type") ?? "application/json" },
  });
}
