import { afterEach, describe, expect, it, vi } from "vitest";

import { GET } from "./route";

describe("GET /api/v1/session/tenant", () => {
  afterEach(() => vi.unstubAllGlobals());

  it("forwards the opaque session and optional tenant probe", async () => {
    const upstream = vi.fn().mockResolvedValue(
      new Response(JSON.stringify({ tenantId: "tenant-1" }), {
        status: 200,
        headers: { "content-type": "application/json" },
      }),
    );
    vi.stubGlobal("fetch", upstream);

    const response = await GET(
      new Request("http://web/api/v1/session/tenant?tenantId=tenant-2", {
        headers: { cookie: "gl_session=opaque" },
      }),
    );

    expect(response.status).toBe(200);
    const [url, options] = upstream.mock.calls[0];
    expect(String(url)).toContain("tenantId=tenant-2");
    expect(options.headers.cookie).toBe("gl_session=opaque");
  });
});
