// @vitest-environment jsdom

import { cleanup, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

import { SuppliersPage } from "./suppliers-page";

describe("procurement suppliers experience", () => {
  afterEach(() => {
    cleanup();
    vi.unstubAllGlobals();
  });

  it("exposes accessible supplier and offer states", () => {
    render(<SuppliersPage initial={{ kind: "ready", suppliers: [], offers: [] }} />);

    expect(screen.getByRole("heading", { name: /procurement/i })).toBeTruthy();
    expect(screen.getByLabelText(/supplier name/i)).toBeTruthy();
    expect(screen.getByLabelText(/supplier code/i)).toBeTruthy();
    expect(screen.getByText(/no suppliers configured/i)).toBeTruthy();
    expect(screen.getByText(/no offers configured/i)).toBeTruthy();
  });

  it("creates a supplier and refreshes the visible list", async () => {
    const user = userEvent.setup();
    const supplier = {
      supplierId: "supplier-1",
      name: "North Market",
      code: "NORTH",
      status: "active" as const,
    };
    const fetcher = vi.fn()
      .mockResolvedValueOnce(Response.json(supplier))
      .mockResolvedValueOnce(Response.json([supplier]))
      .mockResolvedValueOnce(Response.json([]));
    vi.stubGlobal("fetch", fetcher);
    render(<SuppliersPage initial={{ kind: "ready", suppliers: [], offers: [] }} />);

    await user.type(screen.getByLabelText(/supplier name/i), "North Market");
    await user.type(screen.getByLabelText(/supplier code/i), "north");
    await user.click(screen.getByRole("button", { name: /add supplier/i }));

    expect(await screen.findByText("Saved")).toBeTruthy();
    expect(await screen.findByText("NORTH")).toBeTruthy();
  });
});
