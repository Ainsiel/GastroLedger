// @vitest-environment jsdom

import { cleanup, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

import { ProductionPage } from "./production-page";

describe("production batch experience", () => {
  afterEach(() => {
    cleanup();
    vi.unstubAllGlobals();
  });

  it("posts a batch and announces the prepared lot", async () => {
    const user = userEvent.setup();
    vi.stubGlobal(
      "fetch",
      vi.fn().mockImplementation((input: RequestInfo | URL) => Promise.resolve(
        String(input).includes("/expiry-alerts") ? Response.json([]) : Response.json({
          productionBatchId: "production-1",
          inventoryTransactionId: "transaction-1",
          outputLotId: "lot-1",
          batchNumber: "BATCH-001",
          status: "posted",
          recipeVersionId: "recipe-version-1",
          expectedYield: "10",
          actualYield: "8",
          varianceQuantity: "-2",
          varianceReason: "trim loss",
          consumedQuantity: "12",
        })),
      ),
    );
    render(<ProductionPage />);

    await user.type(screen.getByLabelText(/idempotency key/i), "production-001");
    await user.type(screen.getByLabelText(/batch number/i), "BATCH-001");
    await user.type(screen.getByLabelText(/^warehouse id$/i), "warehouse-1");
    await user.type(screen.getByLabelText(/recipe version id/i), "recipe-version-1");
    await user.type(screen.getByLabelText(/actual yield/i), "8");
    await user.type(screen.getByLabelText(/prepared lot code/i), "PREP-001");
    await user.type(screen.getByLabelText(/produced on/i), "2026-06-20");
    await user.type(screen.getByLabelText(/variance reason/i), "trim loss");
    await user.click(screen.getByRole("button", { name: /post production batch/i }));

    expect(await screen.findByText(/batch BATCH-001 posted/i)).toBeTruthy();
    expect(screen.getByText(/8 produced from 12 consumed/i)).toBeTruthy();
  });

  it("preserves input and exposes shortage correlation", async () => {
    const user = userEvent.setup();
    vi.stubGlobal(
      "fetch",
      vi.fn().mockImplementation((input: RequestInfo | URL) => Promise.resolve(
        String(input).includes("/expiry-alerts") ? Response.json([]) : Response.json(
          {
            type: "inventory.insufficient_stock",
            title: "The request could not be completed",
            status: 409,
            correlationId: "shortage-123",
            errors: [],
          },
          { status: 409 },
        )),
      ),
    );
    render(<ProductionPage />);

    await user.type(screen.getByLabelText(/idempotency key/i), "production-002");
    await user.type(screen.getByLabelText(/batch number/i), "BATCH-002");
    await user.type(screen.getByLabelText(/^warehouse id$/i), "warehouse-1");
    await user.type(screen.getByLabelText(/recipe version id/i), "recipe-version-1");
    await user.type(screen.getByLabelText(/actual yield/i), "8");
    await user.type(screen.getByLabelText(/prepared lot code/i), "PREP-002");
    await user.type(screen.getByLabelText(/produced on/i), "2026-06-20");
    await user.click(screen.getByRole("button", { name: /post production batch/i }));

    expect((await screen.findByRole("alert")).textContent).toMatch(/insufficient stock/i);
    expect(screen.getByRole("alert").textContent).toMatch(/shortage-123/i);
    expect((screen.getByLabelText(/batch number/i) as HTMLInputElement).value).toBe("BATCH-002");
  });
});
