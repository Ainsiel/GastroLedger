const apiBaseUrl = process.env.API_BASE_URL ?? "http://api:8000";

export async function POST(request: Request) {
  try {
    const upstream = await fetch(`${apiBaseUrl}/api/v1/session/login`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: await request.text(),
      cache: "no-store",
    });
    const body = await upstream.text();
    JSON.parse(body);
    const headers = new Headers({
      "content-type": upstream.headers.get("content-type") ?? "application/json",
    });
    const cookie = upstream.headers.get("set-cookie");
    if (cookie) headers.set("set-cookie", cookie);
    return new Response(body, { status: upstream.status, headers });
  } catch {
    return Response.json(
      {
        type: "platform.login_upstream_unavailable",
        title: "The request could not be completed",
        status: 500,
        correlationId: crypto.randomUUID(),
        errors: [],
      },
      { status: 500 },
    );
  }
}
