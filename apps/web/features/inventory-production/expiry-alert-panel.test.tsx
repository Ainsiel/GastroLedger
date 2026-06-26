// @vitest-environment jsdom
import { cleanup, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

import { ExpiryAlertPanel } from "./expiry-alert-panel";

const alert = {
  alertId: "alert-1", warehouseId: "warehouse-1", lotId: "lot-1", lotCode: "LOT-001",
  expiryDate: "2026-06-23", status: "active", ruleKey: "expiry-within-3-days-v1",
  createdAt: "2026-06-21T12:00:00Z", acknowledgedBy: null,
  acknowledgedAt: null, actionNote: null,
};

describe("expiry alerts", () => {
  afterEach(() => { cleanup(); vi.unstubAllGlobals(); });

  it("shows active alerts and acknowledgement evidence", async () => {
    const user = userEvent.setup();
    const fetch = vi.fn()
      .mockResolvedValueOnce(Response.json([alert]))
      .mockResolvedValueOnce(Response.json({
        ...alert, status: "acknowledged", acknowledgedBy: "user-1",
        acknowledgedAt: "2026-06-21T13:00:00Z", actionNote: "Moved to prep",
      }));
    vi.stubGlobal("fetch", fetch);
    render(<ExpiryAlertPanel />);

    expect(await screen.findByText("LOT-001")).toBeTruthy();
    await user.type(screen.getByLabelText(/action note/i), "Moved to prep");
    await user.click(screen.getByRole("button", { name: /^acknowledge$/i }));
    expect(await screen.findByText(/moved to prep/i)).toBeTruthy();
  });

  it("preserves the action note on a stale conflict", async () => {
    const user = userEvent.setup();
    vi.stubGlobal("fetch", vi.fn()
      .mockResolvedValueOnce(Response.json([alert]))
      .mockResolvedValueOnce(Response.json({
        type: "inventory.expiry_alert_conflict", title: "Conflict", status: 409,
        correlationId: "expiry-conflict", errors: [],
      }, { status: 409 })));
    render(<ExpiryAlertPanel />);

    await screen.findByText("LOT-001");
    const note = screen.getByLabelText(/action note/i) as HTMLInputElement;
    await user.type(note, "Checking stock");
    await user.click(screen.getByRole("button", { name: /^acknowledge$/i }));
    expect((await screen.findByRole("alert")).textContent).toMatch(/expiry-conflict/);
    expect(note.value).toBe("Checking stock");
  });
});
