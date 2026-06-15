import { describe, expect, it } from "vitest";

import { loadOperatingScope, operatingRequest } from "./operating-scope";

describe("platform operating scope API consumption", () => {
  it("loads session-scoped settings and branches without a tenant selector", async () => {
    const calls: string[] = [];
    const fetcher = async (input: string | URL | Request) => {
      calls.push(String(input));
      if (String(input).endsWith("/tenant/settings")) {
        return Response.json({
          locale: "es",
          baseCurrency: "CLP",
          branchLimit: 2,
          branchCount: 1,
        });
      }
      return Response.json([
        {
          branchId: "branch-1",
          name: "Downtown",
          code: "MAIN",
          warehouses: [],
        },
      ]);
    };

    const result = await loadOperatingScope(fetcher as typeof fetch);

    expect(result.kind).toBe("ready");
    expect(result.kind === "ready" && result.settings.baseCurrency).toBe("CLP");
    expect(calls).toEqual(["/api/v1/tenant/settings", "/api/v1/branches"]);
  });

  it("normalizes typed problems and unavailable proxies into visible outcomes", async () => {
    const conflict = await operatingRequest(
      "/api/v1/branches",
      { method: "POST", body: JSON.stringify({ name: "Duplicate", code: "MAIN" }) },
      async () =>
        Response.json(
          {
            type: "platform.code_conflict",
            title: "The request could not be completed",
            status: 409,
            correlationId: "conflict-1",
            errors: [],
          },
          { status: 409 },
        ),
    );
    const unavailable = await operatingRequest(
      "/api/v1/branches",
      { method: "POST" },
      async () => {
        throw new Error("offline");
      },
    );

    expect(conflict).toEqual({
      kind: "conflict",
      message: "That code is already used in this scope.",
      correlationId: "conflict-1",
    });
    expect(unavailable).toEqual({
      kind: "unexpected",
      message: "The operating scope could not be updated.",
    });
  });
});
