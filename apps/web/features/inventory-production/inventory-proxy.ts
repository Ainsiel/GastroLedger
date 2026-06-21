import type { ApiProblem } from "@gastroledger/api-contract";

const apiBaseUrl = process.env.API_BASE_URL ?? "http://api:8000";

export async function proxyInventoryRequest(
  request: Request,
  upstreamPath: string,
): Promise<Response> {
  try {
    const body = request.method === "GET" ? undefined : await request.text();
    const upstream = await fetch(`${apiBaseUrl}${upstreamPath}`, {
      method: request.method,
      headers: {
        cookie: request.headers.get("cookie") ?? "",
        "content-type": "application/json",
      },
      ...(body === undefined ? {} : { body }),
      cache: "no-store",
    });
    const text = await upstream.text();
    JSON.parse(text);
    return new Response(text, {
      status: upstream.status,
      headers: { "content-type": "application/json" },
    });
  } catch {
    return Response.json(
      {
        type: "inventory.upstream_unavailable",
        title: "The request could not be completed",
        status: 500,
        correlationId: crypto.randomUUID(),
        errors: [],
      } satisfies ApiProblem,
      { status: 500 },
    );
  }
}
