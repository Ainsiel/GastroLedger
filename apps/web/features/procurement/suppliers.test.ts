import { describe, expect, it } from "vitest";

import { loadProcurementCatalog, procurementRequest } from "./suppliers";

describe("procurement API consumption", () => {
  it("loads session-scoped suppliers and offers without a tenant selector", async () => {
    const calls: string[] = [];
    const fetcher = async (input: string | URL | Request) => {
      calls.push(String(input));
      if (String(input).endsWith("/procurement/suppliers")) {
        return Response.json([
          {
            supplierId: "supplier-1",
            name: "North Market",
            code: "NORTH",
            status: "active",
          },
        ]);
      }
      return Response.json([
        {
          supplierOfferId: "offer-1",
          supplierId: "supplier-1",
          ingredientId: null,
          purchaseUnitId: "unit-1",
          price: "12.5",
          currency: "USD",
          effectiveFrom: "2026-06-16",
          effectiveUntil: null,
        },
      ]);
    };

    const result = await loadProcurementCatalog(fetcher as typeof fetch);

    expect(result.kind).toBe("ready");
    expect(result.kind === "ready" && result.suppliers[0].code).toBe("NORTH");
    expect(calls).toEqual(["/api/v1/procurement/suppliers", "/api/v1/procurement/offers"]);
  });

  it("normalizes overlap and validation problems into visible outcomes", async () => {
    const overlap = await procurementRequest(
      "/api/v1/procurement/offers",
      { method: "POST", body: JSON.stringify({ price: "12.50" }) },
      async () =>
        Response.json(
          {
            type: "procurement.offer_overlap",
            title: "The request could not be completed",
            status: 409,
            correlationId: "conflict-1",
            errors: [],
          },
          { status: 409 },
        ),
    );

    expect(overlap).toEqual({
      kind: "conflict",
      message: "That supplier offer overlaps an existing effective date range.",
      correlationId: "conflict-1",
    });
  });
});
