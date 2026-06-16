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
    render(<MenuCatalogPage initial={{ kind: "ready", units: [], ingredients: [] }} />);

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
      .mockResolvedValueOnce(Response.json([archivedIngredient]));
    vi.stubGlobal("fetch", fetcher);
    render(
      <MenuCatalogPage
        initial={{
          kind: "ready",
          units,
          ingredients: [{ ...archivedIngredient, status: "active", availableForNewUse: true }],
        }}
      />,
    );

    await user.click(screen.getByRole("button", { name: /archive flour/i }));
    await user.click(screen.getByRole("button", { name: /confirm archive/i }));

    const result = (await screen.findByText("Saved")).closest('[role="alert"]');
    await waitFor(() => expect(document.activeElement).toBe(result));
  });
});
