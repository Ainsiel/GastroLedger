const apiBaseUrl = process.env.API_BASE_URL ?? "http://api:8000";

export async function POST(request: Request) {
  const upstream = await fetch(`${apiBaseUrl}/api/v1/tenants/register`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: await request.text(),
    cache: "no-store",
  });
  const headers = new Headers({
    "content-type": upstream.headers.get("content-type") ?? "application/json",
  });
  const cookie = upstream.headers.get("set-cookie");
  if (cookie) {
    headers.set("set-cookie", cookie);
  }
  return new Response(await upstream.text(), { status: upstream.status, headers });
}
