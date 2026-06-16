import { afterEach, describe, expect, it, vi } from "vitest";

import { proxyMenuCatalogRequest } from "./menu-proxy";

describe("menu catalog proxy", () => {
  afterEach(() => vi.unstubAllGlobals());

  it("forwards the opaque session, method and body to FastAPI", async () => {
    const upstream = vi.fn().mockResolvedValue(
      Response.json({ name: "Gram", code: "G", dimension: "mass" }, { status: 201 }),
    );
    vi.stubGlobal("fetch", upstream);

    const response = await proxyMenuCatalogRequest(
      new Request("http://web/api/v1/menu/units", {
        method: "POST",
        headers: { cookie: "gl_session=opaque", "content-type": "application/json" },
        body: JSON.stringify({ name: "Gram", code: "G", dimension: "mass" }),
      }),
      "/api/v1/menu/units",
    );

    expect(response.status).toBe(201);
    const [url, init] = upstream.mock.calls[0];
    expect(String(url)).toContain("/api/v1/menu/units");
    expect(init.method).toBe("POST");
    expect(init.headers.cookie).toBe("gl_session=opaque");
    expect(init.body).toContain("Gram");
  });

  it("returns a typed unexpected problem when FastAPI is unavailable", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new Error("offline")));

    const response = await proxyMenuCatalogRequest(
      new Request("http://web/api/v1/menu/units"),
      "/api/v1/menu/units",
    );

    expect(response.status).toBe(500);
    expect((await response.json()).type).toBe("menu.catalog_upstream_unavailable");
  });
});
