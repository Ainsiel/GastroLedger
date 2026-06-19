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

  it("exposes supplier receipt fields and preserves rejected input", async () => {
    const user = userEvent.setup();
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        Response.json(
          {
            type: "procurement.receipt_rejected",
            title: "The request could not be completed",
            status: 409,
            correlationId: "receipt-rejected",
            errors: [{ field: "lines[0].temperature", code: "out_of_range", detail: "review" }],
          },
          { status: 409 },
        ),
      ),
    );
    render(<SuppliersPage initial={{ kind: "ready", suppliers: [], offers: [] }} />);

    await user.type(screen.getByLabelText(/receipt idempotency key/i), "receive-001");
    await user.type(screen.getByLabelText(/order reference/i), "PO-001");
    await user.type(screen.getByLabelText(/receipt supplier id/i), "supplier-1");
    await user.type(screen.getByLabelText(/warehouse id/i), "warehouse-1");
    await user.type(screen.getByLabelText(/receipt ingredient id/i), "ingredient-1");
    await user.type(screen.getByLabelText(/receipt purchase unit id/i), "unit-1");
    await user.type(screen.getByLabelText(/lot code/i), "LOT-001");
    await user.type(screen.getByLabelText(/delivered quantity/i), "5");
    await user.type(document.querySelector("#receipt-received") as HTMLInputElement, "2026-06-19");
    await user.type(document.querySelector("#receipt-expiry") as HTMLInputElement, "2026-07-19");
    await user.click(screen.getByRole("button", { name: /receive delivery/i }));

    expect(await screen.findByText(/temperature, duplicate lot or tolerance/i)).toBeTruthy();
    expect((screen.getByLabelText(/lot code/i) as HTMLInputElement).value).toBe("LOT-001");
  });
});
