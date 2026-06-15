import { afterEach, describe, expect, it, vi } from "vitest";

import { POST, registrationGlobalLimiter, registrationIdentityLimiter } from "./route";

describe("POST /api/v1/tenants/register", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
    registrationGlobalLimiter.reset();
    registrationIdentityLimiter.reset();
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
        body: JSON.stringify({ tenantSlug: "tenant-1" }),
      }),
    );

    expect(response.status).toBe(201);
    expect(response.headers.get("set-cookie")).toContain("gl_session=opaque");
    expect(response.headers.get("set-cookie")).toContain("gl_registration_identity=");
    expect(upstream).toHaveBeenCalledOnce();
    expect(upstream.mock.calls[0][1].headers).not.toHaveProperty(
      "x-gastroledger-registration-key",
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

  it("does not allow client-controlled headers to evade the public edge limit", async () => {
    const upstream = vi
      .fn()
      .mockImplementation(async () =>
        Response.json({ type: "platform.validation_error" }, { status: 422 }),
      );
    vi.stubGlobal("fetch", upstream);

    const requests = Array.from({ length: 6 }, (_, index) =>
        new Request("http://web/api/v1/tenants/register", {
          method: "POST",
          headers: {
            "x-forwarded-for": `192.0.2.${index}`,
            "x-real-ip": `198.51.100.${index}`,
            "user-agent": `rotating-agent-${index}`,
          },
          body: "{}",
        }),
    );
    const responses = [];
    for (const request of requests) responses.push(await POST(request));

    expect(responses.at(-1)?.status).toBe(429);
    expect(upstream).toHaveBeenCalledTimes(5);
  });

  it("does not allow forged registration identity cookies to evade the limit", async () => {
    const upstream = vi
      .fn()
      .mockImplementation(async () =>
        Response.json({ type: "platform.validation_error" }, { status: 422 }),
      );
    vi.stubGlobal("fetch", upstream);

    const responses = [];
    for (let index = 0; index < 6; index += 1) {
      responses.push(
        await POST(
          new Request("http://web/api/v1/tenants/register", {
            method: "POST",
            headers: { cookie: `gl_registration_identity=forged-${index}.signature` },
            body: "{}",
          }),
        ),
      );
    }

    expect(responses.at(-1)?.status).toBe(429);
    expect(upstream).toHaveBeenCalledTimes(5);
  });

  it("uses a valid signed registration identity after it is issued", async () => {
    const upstream = vi
      .fn()
      .mockImplementation(async () =>
        Response.json({ type: "platform.validation_error" }, { status: 422 }),
      );
    vi.stubGlobal("fetch", upstream);

    const initial = await POST(
      new Request("http://web/api/v1/tenants/register", { method: "POST", body: "{}" }),
    );
    const identityCookie = initial.headers
      .get("set-cookie")
      ?.match(/gl_registration_identity=([^;]+)/)?.[1];
    expect(identityCookie).toBeTruthy();

    registrationIdentityLimiter.reset();
    for (let index = 0; index < 5; index += 1) {
      await POST(
        new Request("http://web/api/v1/tenants/register", {
          method: "POST",
          headers: { cookie: `gl_registration_identity=${identityCookie}` },
          body: "{}",
        }),
      );
    }
    const limited = await POST(
      new Request("http://web/api/v1/tenants/register", {
        method: "POST",
        headers: { cookie: `gl_registration_identity=${identityCookie}` },
        body: "{}",
      }),
    );

    expect(limited.status).toBe(429);
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
