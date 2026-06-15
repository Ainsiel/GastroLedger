import type { ApiProblem } from "@gastroledger/api-contract";
import { createHmac, randomBytes, timingSafeEqual } from "node:crypto";

const apiBaseUrl = process.env.API_BASE_URL ?? "http://api:8000";
const maxRegistrationBodyBytes = 16 * 1024;
const registrationIdentityCookie = "gl_registration_identity";
const registrationIdentitySecret = randomBytes(32);

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

export const registrationIdentityLimiter = new EdgeRateLimiter();
export const registrationGlobalLimiter = new EdgeRateLimiter(100);

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

function signIdentity(identity: string): string {
  return createHmac("sha256", registrationIdentitySecret).update(identity).digest("base64url");
}

function registrationIdentity(request: Request): string | null {
  const cookie = request.headers
    .get("cookie")
    ?.split(";")
    .map((part) => part.trim())
    .find((part) => part.startsWith(`${registrationIdentityCookie}=`))
    ?.slice(registrationIdentityCookie.length + 1);
  if (!cookie) return null;

  const [identity, signature, ...extra] = cookie.split(".");
  if (!identity || !signature || extra.length > 0) return null;
  const expected = Buffer.from(signIdentity(identity));
  const provided = Buffer.from(signature);
  if (expected.length !== provided.length || !timingSafeEqual(expected, provided)) return null;
  return identity;
}

function issueRegistrationIdentity(): string {
  const identity = randomBytes(18).toString("base64url");
  const secure =
    process.env.GL_ENVIRONMENT &&
    !["development", "integration"].includes(process.env.GL_ENVIRONMENT);
  return [
    `${registrationIdentityCookie}=${identity}.${signIdentity(identity)}`,
    "Max-Age=86400",
    "HttpOnly",
    "SameSite=Strict",
    "Path=/api/v1/tenants/register",
    secure ? "Secure" : "",
  ]
    .filter(Boolean)
    .join("; ");
}

function withRegistrationIdentity(response: Response, cookie: string | null): Response {
  if (cookie) response.headers.append("set-cookie", cookie);
  return response;
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
  const identity = registrationIdentity(request);
  const identityCookie = identity ? null : issueRegistrationIdentity();
  if (
    !registrationGlobalLimiter.allow("global") ||
    !registrationIdentityLimiter.allow(identity ? `identity:${identity}` : "anonymous")
  ) {
    const response = problem(429, "platform.registration_rate_limited");
    response.headers.set("retry-after", "60");
    return response;
  }

  const body = await boundedBody(request);
  if (body instanceof Response) return withRegistrationIdentity(body, identityCookie);

  try {
    const upstream = await fetch(`${apiBaseUrl}/api/v1/tenants/register`, {
      method: "POST",
      headers: {
        "content-type": "application/json",
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
    return withRegistrationIdentity(
      new Response(upstreamText, { status: upstream.status, headers }),
      identityCookie,
    );
  } catch {
    return withRegistrationIdentity(
      problem(500, "platform.registration_upstream_unavailable"),
      identityCookie,
    );
  }
}
