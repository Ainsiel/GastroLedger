import { afterEach, describe, expect, it, vi } from "vitest";

import { POST } from "./route";

describe("POST /api/v1/session/login", () => {
  afterEach(() => vi.unstubAllGlobals());

  it("forwards credentials and the scoped session cookie", async () => {
    const upstream = vi.fn().mockResolvedValue(
      new Response(JSON.stringify({ tenantName: "Sabor Central" }), {
        status: 200,
        headers: {
          "content-type": "application/json",
          "set-cookie": "gl_session=opaque; HttpOnly; SameSite=Strict",
        },
      }),
    );
    vi.stubGlobal("fetch", upstream);

    const response = await POST(
      new Request("http://web/api/v1/session/login", {
        method: "POST",
        body: JSON.stringify({ email: "admin@example.com", password: "StrongPassword123" }),
      }),
    );

    expect(response.status).toBe(200);
    expect(response.headers.get("set-cookie")).toContain("gl_session=opaque");
    expect(upstream.mock.calls[0][1].body).toContain("admin@example.com");
  });
});
