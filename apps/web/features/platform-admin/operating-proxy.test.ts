import { afterEach, describe, expect, it, vi } from "vitest";

import { proxyOperatingRequest } from "./operating-proxy";

describe("platform operating scope proxy", () => {
  afterEach(() => vi.unstubAllGlobals());

  it("forwards the opaque session, method and body to FastAPI", async () => {
    const upstream = vi.fn().mockResolvedValue(
      Response.json({ name: "Downtown", code: "MAIN" }, { status: 201 }),
    );
    vi.stubGlobal("fetch", upstream);

    const response = await proxyOperatingRequest(
      new Request("http://web/api/v1/branches", {
        method: "POST",
        headers: { cookie: "gl_session=opaque", "content-type": "application/json" },
        body: JSON.stringify({ name: "Downtown", code: "MAIN" }),
      }),
      "/api/v1/branches",
    );

    expect(response.status).toBe(201);
    const [url, init] = upstream.mock.calls[0];
    expect(String(url)).toContain("/api/v1/branches");
    expect(init.method).toBe("POST");
    expect(init.headers.cookie).toBe("gl_session=opaque");
    expect(init.body).toContain("Downtown");
  });

  it("forwards Set-Cookie from invitation acceptance responses", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        Response.json(
          { tenantId: "tenant-1", actorId: "actor-1", tenantName: "Sabor", tenantSlug: "sabor" },
          { headers: { "set-cookie": "gl_session=accepted; Path=/; HttpOnly" } },
        ),
      ),
    );

    const response = await proxyOperatingRequest(
      new Request("http://web/api/v1/users/invitations/accept", {
        method: "POST",
        body: JSON.stringify({ manualShareToken: "token", password: "StrongPassword123" }),
      }),
      "/api/v1/users/invitations/accept",
    );

    expect(response.headers.get("set-cookie")).toContain("gl_session=accepted");
  });

  it("returns a typed unexpected problem when FastAPI is unavailable", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new Error("offline")));

    const response = await proxyOperatingRequest(
      new Request("http://web/api/v1/branches"),
      "/api/v1/branches",
    );

    expect(response.status).toBe(500);
    expect((await response.json()).type).toBe("platform.operating_scope_upstream_unavailable");
  });
});
