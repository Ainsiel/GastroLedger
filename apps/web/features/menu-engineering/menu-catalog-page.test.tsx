// @vitest-environment jsdom

import { cleanup, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

import { MenuCatalogPage } from "./menu-catalog-page";

describe("menu catalog experience", () => {
  afterEach(() => {
    cleanup();
    vi.unstubAllGlobals();
  });

  it("exposes accessible unit and ingredient catalog states", () => {
    render(<MenuCatalogPage initial={{ kind: "ready", units: [], ingredients: [], subRecipes: [], menuItems: [] }} />);

    expect(screen.getByRole("heading", { name: /menu engineering/i })).toBeTruthy();
    expect(screen.getByLabelText(/unit name/i)).toBeTruthy();
    expect(screen.getByLabelText(/unit code/i)).toBeTruthy();
    expect(screen.getByText(/no units configured/i)).toBeTruthy();
    expect(screen.getByText(/no ingredients configured/i)).toBeTruthy();
  });

  it("requires confirmation before archiving an active ingredient", async () => {
    const user = userEvent.setup();
    render(
      <MenuCatalogPage
        initial={{
          kind: "ready",
          units: [
            {
              unitId: "unit-1",
              name: "Kilogram",
              code: "KG",
              dimension: "mass",
              conversions: [],
            },
          ],
          ingredients: [
            {
              ingredientId: "ingredient-1",
              name: "Flour",
              code: "FLOUR",
              purchaseUnitId: "unit-1",
              consumptionUnitId: "unit-1",
              shelfLifeDays: 180,
              criticalStockQuantity: "12.5",
              status: "active",
              availableForNewUse: true,
            },
          ],
          subRecipes: [],
          menuItems: [],
        }}
      />,
    );

    const archive = screen.getByRole("button", { name: /archive flour/i });
    archive.focus();
    await user.click(archive);

    expect(screen.getByText(/archive flour\?/i)).toBeTruthy();
    const confirm = screen.getByRole("button", { name: /confirm archive/i });
    expect(document.activeElement).toBe(confirm);

    await user.click(screen.getByRole("button", { name: /cancel/i }));

    expect(document.activeElement).toBe(screen.getByRole("button", { name: /archive flour/i }));
  });

  it("moves focus to the result after archiving", async () => {
    const user = userEvent.setup();
    const archivedIngredient = {
      ingredientId: "ingredient-1",
      name: "Flour",
      code: "FLOUR",
      purchaseUnitId: "unit-1",
      consumptionUnitId: "unit-1",
      shelfLifeDays: 180,
      criticalStockQuantity: "12.5",
      status: "archived" as const,
      availableForNewUse: false,
    };
    const units = [
      {
        unitId: "unit-1",
        name: "Kilogram",
        code: "KG",
        dimension: "mass" as const,
        conversions: [],
      },
    ];
    const fetcher = vi.fn()
      .mockResolvedValueOnce(Response.json(archivedIngredient))
      .mockResolvedValueOnce(Response.json(units))
      .mockResolvedValueOnce(Response.json([archivedIngredient]))
      .mockResolvedValueOnce(Response.json([]))
      .mockResolvedValueOnce(Response.json([]));
    vi.stubGlobal("fetch", fetcher);
    render(
      <MenuCatalogPage
        initial={{
          kind: "ready",
          units,
          ingredients: [{ ...archivedIngredient, status: "active", availableForNewUse: true }],
          subRecipes: [],
          menuItems: [],
        }}
      />,
    );

    await user.click(screen.getByRole("button", { name: /archive flour/i }));
    await user.click(screen.getByRole("button", { name: /confirm archive/i }));

    const result = (await screen.findByText("Saved")).closest('[role="alert"]');
    await waitFor(() => expect(document.activeElement).toBe(result));
  });

  it("preserves sub-recipe draft input after recoverable approval errors", async () => {
    const user = userEvent.setup();
    const unit = {
      unitId: "unit-1",
      name: "Kilogram",
      code: "KG",
      dimension: "mass" as const,
      conversions: [],
    };
    const ingredient = {
      ingredientId: "ingredient-1",
      name: "Tomato",
      code: "TOMATO",
      purchaseUnitId: "unit-1",
      consumptionUnitId: "unit-1",
      shelfLifeDays: 12,
      criticalStockQuantity: "5",
      status: "active" as const,
      availableForNewUse: true,
    };
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        Response.json(
          {
            type: "menu.recipe_graph_invalid",
            title: "The request could not be completed",
            status: 409,
            correlationId: "recipe-conflict",
            errors: [],
          },
          { status: 409 },
        ),
      ),
    );

    render(
      <MenuCatalogPage
        initial={{
          kind: "ready",
          units: [unit],
          ingredients: [ingredient],
          subRecipes: [],
          menuItems: [],
        }}
      />,
    );

    await user.type(screen.getByLabelText(/sub-recipe name/i), "Tomato base");
    await user.type(screen.getByLabelText(/sub-recipe code/i), "tomato-base");
    await user.type(screen.getByLabelText(/^version$/i), "v1");
    await user.type(screen.getByLabelText(/yield quantity/i), "2");
    await user.type(screen.getByLabelText(/component quantity/i), "4");
    await user.type(document.querySelector("#sub-recipe-effective") as HTMLInputElement, "2026-06-19");
    await user.click(screen.getByRole("button", { name: /approve sub-recipe/i }));

    expect(await screen.findByText(/approved nesting depth/i)).toBeTruthy();
    expect((screen.getByLabelText(/sub-recipe name/i) as HTMLInputElement).value).toBe("Tomato base");
    expect((screen.getByLabelText(/component quantity/i) as HTMLInputElement).value).toBe("4");
  });

  it("shows menu item approval and branch margin controls", async () => {
    const user = userEvent.setup();
    const unit = {
      unitId: "unit-1",
      name: "Serving",
      code: "EA",
      dimension: "count" as const,
      conversions: [],
    };
    const subRecipe = {
      recipeId: "recipe-1",
      recipeVersionId: "sub-version-1",
      name: "Tomato base",
      code: "TOMATO-BASE",
      version: "v1",
      yieldQuantity: "1",
      yieldUnitId: "unit-1",
      effectiveFrom: "2026-06-19",
      status: "approved" as const,
      isActive: true,
      components: [],
      costSnapshot: { totalCost: "4", status: "current" as const },
    };
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        Response.json(
          {
            type: "menu.recipe_missing_cost",
            title: "The request could not be completed",
            status: 409,
            correlationId: "missing-cost",
            errors: [],
          },
          { status: 409 },
        ),
      ),
    );

    render(
      <MenuCatalogPage
        initial={{
          kind: "ready",
          units: [unit],
          ingredients: [],
          subRecipes: [subRecipe],
          menuItems: [],
        }}
      />,
    );

    await user.type(screen.getByLabelText(/menu item name/i), "Lunch Bowl");
    await user.type(screen.getByLabelText(/menu item code/i), "lunch-bowl");
    await user.type(screen.getByLabelText(/menu item version/i), "v1");
    await user.type(screen.getByLabelText(/menu item serving quantity/i), "1");
    await user.type(screen.getByLabelText(/menu item sub-recipe quantity/i), "1");
    await user.type(document.querySelector("#menu-item-effective") as HTMLInputElement, "2026-06-19");
    await user.click(screen.getByRole("button", { name: /approve menu item/i }));

    expect(await screen.findByText(/supplier offer cost evidence/i)).toBeTruthy();
    expect((screen.getByLabelText(/menu item name/i) as HTMLInputElement).value).toBe("Lunch Bowl");
  });
});
