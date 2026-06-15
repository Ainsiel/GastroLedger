import type { ApiProblem } from "@gastroledger/api-contract";

const apiBaseUrl = process.env.API_BASE_URL ?? "http://api:8000";
const maxRegistrationBodyBytes = 16 * 1024;

class EdgeRateLimiter {
  private windows = new Map<string, { startedAt: number; count: number }>();

  constructor(
    private readonly limit = 5,
    private readonly windowMs = 60_000,
    private readonly maxKeys = 4096,
  ) {}

  allow(key: string, now = Date.now()): boolean {
    const current = this.windows.get(key);
    const window =
      !current || now - current.startedAt >= this.windowMs
        ? { startedAt: now, count: 0 }
        : current;
    if (!current && this.windows.size >= this.maxKeys) {
      const oldest = this.windows.keys().next().value;
      if (oldest) this.windows.delete(oldest);
    }
    this.windows.delete(key);
    this.windows.set(key, { startedAt: window.startedAt, count: window.count + 1 });
    return window.count < this.limit;
  }

  reset() {
    this.windows.clear();
  }
}

export const registrationEdgeLimiter = new EdgeRateLimiter();

function problem(status: number, type: string, errors: ApiProblem["errors"] = []) {
  return Response.json(
    {
      type,
      title: "The request could not be completed",
      status,
      correlationId: crypto.randomUUID(),
      errors,
    } satisfies ApiProblem,
    { status },
  );
}

function registrationClientKey(request: Request): string {
  const forwarded = request.headers.get("x-forwarded-for")?.split(",", 1)[0]?.trim();
  return (
    forwarded ||
    request.headers.get("x-real-ip")?.trim() ||
    request.headers.get("user-agent")?.trim() ||
    "unknown"
  ).slice(0, 256);
}

async function boundedBody(request: Request): Promise<string | Response> {
  const declaredLength = Number(request.headers.get("content-length"));
  if (Number.isFinite(declaredLength) && declaredLength > maxRegistrationBodyBytes) {
    return problem(422, "platform.registration_payload_too_large", [
      { field: "body", code: "too_large", detail: "reduce request size" },
    ]);
  }
  if (!request.body) return "";

  const reader = request.body.getReader();
  const chunks: Uint8Array[] = [];
  let length = 0;
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    length += value.byteLength;
    if (length > maxRegistrationBodyBytes) {
      await reader.cancel();
      return problem(422, "platform.registration_payload_too_large", [
        { field: "body", code: "too_large", detail: "reduce request size" },
      ]);
    }
    chunks.push(value);
  }

  const body = new Uint8Array(length);
  let offset = 0;
  for (const chunk of chunks) {
    body.set(chunk, offset);
    offset += chunk.byteLength;
  }
  return new TextDecoder().decode(body);
}

export async function POST(request: Request) {
  const registrationKey = registrationClientKey(request);
  if (!registrationEdgeLimiter.allow(registrationKey)) {
    const response = problem(429, "platform.registration_rate_limited");
    response.headers.set("retry-after", "60");
    return response;
  }

  const body = await boundedBody(request);
  if (body instanceof Response) return body;

  try {
    const upstream = await fetch(`${apiBaseUrl}/api/v1/tenants/register`, {
      method: "POST",
      headers: {
        "content-type": "application/json",
        "x-gastroledger-registration-key": registrationKey,
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
    return new Response(upstreamText, { status: upstream.status, headers });
  } catch {
    return problem(500, "platform.registration_upstream_unavailable");
  }
}
