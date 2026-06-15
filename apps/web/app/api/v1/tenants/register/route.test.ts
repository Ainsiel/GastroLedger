import { afterEach, describe, expect, it, vi } from "vitest";

import { POST, registrationEdgeLimiter } from "./route";

describe("POST /api/v1/tenants/register", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
    registrationEdgeLimiter.reset();
  });

  it("forwards registration and the scoped session cookie", async () => {
    const upstream = vi.fn().mockResolvedValue(
      new Response(JSON.stringify({ tenantId: "tenant-1" }), {
        status: 201,
        headers: {
          "content-type": "application/json",
          "set-cookie": "gl_session=opaque; HttpOnly; SameSite=Strict",
        },
      }),
    );
    vi.stubGlobal("fetch", upstream);

    const response = await POST(
      new Request("http://web/api/v1/tenants/register", {
        method: "POST",
        headers: { "x-forwarded-for": "192.0.2.10" },
        body: JSON.stringify({ tenantSlug: "tenant-1" }),
      }),
    );

    expect(response.status).toBe(201);
    expect(response.headers.get("set-cookie")).toContain("gl_session=opaque");
    expect(upstream).toHaveBeenCalledOnce();
    expect(upstream.mock.calls[0][1].headers["x-gastroledger-registration-key"]).toBe(
      "192.0.2.10",
    );
  });

  it("rejects a large body before calling FastAPI", async () => {
    const upstream = vi.fn();
    vi.stubGlobal("fetch", upstream);

    const response = await POST(
      new Request("http://web/api/v1/tenants/register", {
        method: "POST",
        body: JSON.stringify({ padding: "x".repeat(17 * 1024) }),
      }),
    );

    expect(response.status).toBe(422);
    expect((await response.json()).type).toBe("platform.registration_payload_too_large");
    expect(upstream).not.toHaveBeenCalled();
  });

  it("rate limits at the public web edge before calling FastAPI", async () => {
    const upstream = vi
      .fn()
      .mockImplementation(async () =>
        Response.json({ type: "platform.validation_error" }, { status: 422 }),
      );
    vi.stubGlobal("fetch", upstream);

    const requests = Array.from(
      { length: 6 },
      () =>
        new Request("http://web/api/v1/tenants/register", {
          method: "POST",
          headers: { "x-forwarded-for": "192.0.2.20" },
          body: "{}",
        }),
    );
    const responses = [];
    for (const request of requests) responses.push(await POST(request));

    expect(responses.at(-1)?.status).toBe(429);
    expect(upstream).toHaveBeenCalledTimes(5);

    const otherClient = await POST(
      new Request("http://web/api/v1/tenants/register", {
        method: "POST",
        headers: { "x-forwarded-for": "192.0.2.21" },
        body: "{}",
      }),
    );
    expect(otherClient.status).toBe(422);
    expect(upstream).toHaveBeenCalledTimes(6);
  });

  it("returns a stable problem when FastAPI is unavailable", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new Error("offline")));

    const response = await POST(
      new Request("http://web/api/v1/tenants/register", {
        method: "POST",
        body: "{}",
      }),
    );

    expect(response.status).toBe(500);
    expect((await response.json()).type).toBe("platform.registration_upstream_unavailable");
  });
});
