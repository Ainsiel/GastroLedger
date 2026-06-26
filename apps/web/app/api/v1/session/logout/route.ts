const apiBaseUrl = process.env.API_BASE_URL ?? "http://api:8000";

export async function POST(request: Request) {
  try {
    const upstream = await fetch(`${apiBaseUrl}/api/v1/session/logout`, {
      method: "POST",
      headers: { cookie: request.headers.get("cookie") ?? "" },
      cache: "no-store",
    });
    const body = await upstream.text();
    const headers = new Headers();
    const contentType = upstream.headers.get("content-type");
    if (contentType) headers.set("content-type", contentType);
    const cookie = upstream.headers.get("set-cookie");
    if (cookie) headers.set("set-cookie", cookie);
    return new Response(upstream.status === 204 ? null : body, {
      status: upstream.status,
      headers,
    });
  } catch {
    return Response.json(
      {
        type: "platform.logout_upstream_unavailable",
        title: "The request could not be completed",
        status: 500,
        correlationId: crypto.randomUUID(),
        errors: [],
      },
      { status: 500 },
    );
  }
}
