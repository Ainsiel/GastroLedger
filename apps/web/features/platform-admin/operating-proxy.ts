import type { ApiProblem } from "@gastroledger/api-contract";

const apiBaseUrl = process.env.API_BASE_URL ?? "http://api:8000";

function unavailableProblem() {
  return Response.json(
    {
      type: "platform.operating_scope_upstream_unavailable",
      title: "The request could not be completed",
      status: 500,
      correlationId: crypto.randomUUID(),
      errors: [],
    } satisfies ApiProblem,
    { status: 500 },
  );
}

export async function proxyOperatingRequest(
  request: Request,
  upstreamPath: string,
): Promise<Response> {
  try {
    const body = request.method === "GET" ? undefined : await request.text();
    const upstream = await fetch(`${apiBaseUrl}${upstreamPath}`, {
      method: request.method,
      headers: {
        cookie: request.headers.get("cookie") ?? "",
        ...(body ? { "content-type": "application/json" } : {}),
      },
      body,
      cache: "no-store",
    });
    const upstreamText = await upstream.text();
    JSON.parse(upstreamText);
    const headers = new Headers({
      "content-type": upstream.headers.get("content-type") ?? "application/json",
    });
    const cookie = upstream.headers.get("set-cookie");
    if (cookie) headers.set("set-cookie", cookie);
    return new Response(upstreamText, {
      status: upstream.status,
      headers,
    });
  } catch {
    return unavailableProblem();
  }
}
