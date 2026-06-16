// @vitest-environment jsdom

import { cleanup, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

import { OperatingScopePage } from "./operating-scope-page";

describe("tenant operating scope experience", () => {
  afterEach(() => {
    cleanup();
    vi.unstubAllGlobals();
  });

  it("exposes accessible settings and an honest empty branch state", () => {
    render(
      <OperatingScopePage
        initial={{
          kind: "ready",
          settings: {
            locale: "es",
            baseCurrency: "CLP",
            branchLimit: 2,
            branchCount: 0,
          },
          branches: [],
        }}
      />,
    );

    expect(screen.getByRole("heading", { name: /organization settings/i })).toBeTruthy();
    expect(screen.getByLabelText(/locale/i)).toBeTruthy();
    expect(screen.getByLabelText(/base currency/i)).toBeTruthy();
    expect(screen.getByText(/no branches configured/i)).toBeTruthy();
    expect(screen.getByRole("button", { name: /create branch/i })).toBeTruthy();
    expect(screen.getByRole("heading", { name: /user invitations and scoped roles/i })).toBeTruthy();
  });

  it("generates a manually shareable branch scoped invitation", async () => {
    const user = userEvent.setup();
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        Response.json(
          {
            invitationId: "invitation-1",
            manualShareToken: "manual-token",
            inviteeLogin: "manager@example.com",
            role: "branch_manager",
            scope: "branch",
            branchId: "branch-1",
            ttlHours: 24,
            expiresAt: "2026-06-16T12:00:00Z",
            status: "pending",
          },
          { status: 201 },
        ),
      ),
    );
    render(
      <OperatingScopePage
        initial={{
          kind: "ready",
          settings: {
            locale: "en",
            baseCurrency: "USD",
            branchLimit: 1,
            branchCount: 1,
          },
          branches: [
            {
              branchId: "branch-1",
              name: "Downtown",
              code: "MAIN",
              warehouses: [],
            },
          ],
        }}
      />,
    );

    await user.type(screen.getByLabelText(/invitee email/i), "manager@example.com");
    await user.click(screen.getByRole("button", { name: /^invite$/i }));

    expect(await screen.findByText(/manual invitation ready/i)).toBeTruthy();
    expect(screen.getByText("manual-token")).toBeTruthy();
  });

  it("requires confirmation before deactivating an active warehouse", async () => {
    const user = userEvent.setup();
    render(
      <OperatingScopePage
        initial={{
          kind: "ready",
          settings: {
            locale: "en",
            baseCurrency: "USD",
            branchLimit: 1,
            branchCount: 1,
          },
          branches: [
            {
              branchId: "branch-1",
              name: "Downtown",
              code: "MAIN",
              warehouses: [
                {
                  warehouseId: "warehouse-1",
                  branchId: "branch-1",
                  name: "Kitchen",
                  code: "KITCHEN",
                  type: "kitchen",
                  status: "active",
                },
              ],
            },
          ],
        }}
      />,
    );

    const deactivate = screen.getByRole("button", { name: /deactivate kitchen/i });
    deactivate.focus();
    await user.click(deactivate);

    expect(screen.getByText(/deactivate kitchen\?/i)).toBeTruthy();
    const confirm = screen.getByRole("button", { name: /confirm deactivation/i });
    expect(document.activeElement).toBe(confirm);

    await user.click(screen.getByRole("button", { name: /cancel/i }));

    expect(document.activeElement).toBe(screen.getByRole("button", { name: /deactivate kitchen/i }));
  });

  it("moves focus to the result after completing warehouse deactivation", async () => {
    const user = userEvent.setup();
    const inactiveWarehouse = {
      warehouseId: "warehouse-1",
      branchId: "branch-1",
      name: "Kitchen",
      code: "KITCHEN",
      type: "kitchen" as const,
      status: "inactive" as const,
    };
    const fetcher = vi.fn()
      .mockResolvedValueOnce(Response.json(inactiveWarehouse))
      .mockResolvedValueOnce(Response.json({
        locale: "en",
        baseCurrency: "USD",
        branchLimit: 1,
        branchCount: 1,
      }))
      .mockResolvedValueOnce(Response.json([{
        branchId: "branch-1",
        name: "Downtown",
        code: "MAIN",
        warehouses: [inactiveWarehouse],
      }]));
    vi.stubGlobal("fetch", fetcher);
    render(
      <OperatingScopePage
        initial={{
          kind: "ready",
          settings: {
            locale: "en",
            baseCurrency: "USD",
            branchLimit: 1,
            branchCount: 1,
          },
          branches: [{
            branchId: "branch-1",
            name: "Downtown",
            code: "MAIN",
            warehouses: [{ ...inactiveWarehouse, status: "active" }],
          }],
        }}
      />,
    );

    await user.click(screen.getByRole("button", { name: /deactivate kitchen/i }));
    await user.click(screen.getByRole("button", { name: /confirm deactivation/i }));

    const result = (await screen.findByText("Saved")).closest('[role="alert"]');
    await waitFor(() => expect(document.activeElement).toBe(result));
  });

  it("shows an authentication-required state without enabled management actions", () => {
    render(<OperatingScopePage initial={{ kind: "unauthorized" }} />);

    expect(screen.getByText(/administrator session is required/i)).toBeTruthy();
    expect(screen.queryByRole("button", { name: /create branch/i })).toBeNull();
  });

  it("disables branch creation when the configured capacity is reached", () => {
    render(
      <OperatingScopePage
        initial={{
          kind: "ready",
          settings: {
            locale: "en",
            baseCurrency: "USD",
            branchLimit: 1,
            branchCount: 1,
          },
          branches: [],
        }}
      />,
    );

    expect(screen.getByText(/branch capacity reached/i)).toBeTruthy();
    expect(screen.getByRole("button", { name: /create branch/i }).hasAttribute("disabled")).toBe(
      true,
    );
  });
});
