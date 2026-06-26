import { afterEach, describe, expect, it, vi } from "vitest";

import { POST } from "./route";

describe("POST /api/v1/session/logout", () => {
  afterEach(() => vi.unstubAllGlobals());

  it("forwards the opaque session and logout cookie", async () => {
    const upstream = vi.fn().mockResolvedValue(
      new Response(null, {
        status: 204,
        headers: { "set-cookie": "gl_session=; Max-Age=0; Path=/" },
      }),
    );
    vi.stubGlobal("fetch", upstream);

    const response = await POST(
      new Request("http://web/api/v1/session/logout", {
        method: "POST",
        headers: { cookie: "gl_session=opaque" },
      }),
    );

    expect(response.status).toBe(204);
    expect(response.headers.get("set-cookie")).toContain("gl_session=");
    expect(upstream.mock.calls[0][1].headers.cookie).toBe("gl_session=opaque");
  });
});
