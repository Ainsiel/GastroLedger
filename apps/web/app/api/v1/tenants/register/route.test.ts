import { afterEach, describe, expect, it, vi } from "vitest";

import { POST } from "./route";

describe("POST /api/v1/tenants/register", () => {
  afterEach(() => vi.unstubAllGlobals());

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
    expect(upstream).toHaveBeenCalledOnce();
  });
});
