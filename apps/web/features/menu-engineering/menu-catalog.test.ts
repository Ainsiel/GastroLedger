import { describe, expect, it } from "vitest";

import { loadMenuCatalog, menuCatalogRequest } from "./menu-catalog";

describe("menu catalog API consumption", () => {
  it("loads session-scoped units and ingredients without a tenant selector", async () => {
    const calls: string[] = [];
    const fetcher = async (input: string | URL | Request) => {
      calls.push(String(input));
      if (String(input).endsWith("/menu/units")) {
        return Response.json([
          {
            unitId: "unit-1",
            name: "Kilogram",
            code: "KG",
            dimension: "mass",
            conversions: [],
          },
        ]);
      }
      if (String(input).endsWith("/menu/ingredients")) {
        return Response.json([
          {
            ingredientId: "ingredient-1",
            name: "Flour",
            code: "FLOUR",
            purchaseUnitId: "unit-1",
            consumptionUnitId: "unit-1",
            shelfLifeDays: 180,
            criticalStockQuantity: "10",
            status: "active",
            availableForNewUse: true,
          },
        ]);
      }
      return Response.json([
        {
          recipeId: "recipe-1",
          recipeVersionId: "version-1",
          name: "Sofrito base",
          code: "SOFRITO-BASE",
          version: "v1",
          yieldQuantity: "2",
          yieldUnitId: "unit-1",
          effectiveFrom: "2026-06-19",
          status: "approved",
          isActive: true,
          components: [],
          costSnapshot: { totalCost: "14", status: "current" },
        },
      ]);
    };

    const result = await loadMenuCatalog(fetcher as typeof fetch);

    expect(result.kind).toBe("ready");
    expect(result.kind === "ready" && result.units[0].code).toBe("KG");
    expect(calls).toEqual([
      "/api/v1/menu/units",
      "/api/v1/menu/ingredients",
      "/api/v1/menu/recipes/sub-recipes",
    ]);
  });

  it("normalizes duplicate and validation problems into visible outcomes", async () => {
    const duplicate = await menuCatalogRequest(
      "/api/v1/menu/units",
      { method: "POST", body: JSON.stringify({ name: "Gram", code: "G" }) },
      async () =>
        Response.json(
          {
            type: "menu.code_conflict",
            title: "The request could not be completed",
            status: 409,
            correlationId: "conflict-1",
            errors: [],
          },
          { status: 409 },
        ),
    );

    expect(duplicate).toEqual({
      kind: "conflict",
      message: "That code or effective-dated factor already exists.",
      correlationId: "conflict-1",
    });

    const graph = await menuCatalogRequest(
      "/api/v1/menu/recipes/sub-recipes",
      { method: "POST", body: JSON.stringify({}) },
      async () =>
        Response.json(
          {
            type: "menu.recipe_graph_invalid",
            title: "The request could not be completed",
            status: 409,
            correlationId: "graph-1",
            errors: [],
          },
          { status: 409 },
        ),
    );

    expect(graph).toEqual({
      kind: "conflict",
      message: "Recipe approval would create a cycle or exceed the approved nesting depth.",
      correlationId: "graph-1",
    });
  });
});
