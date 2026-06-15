// @vitest-environment jsdom

import { cleanup, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it } from "vitest";

import { OperatingScopePage } from "./operating-scope-page";

describe("tenant operating scope experience", () => {
  afterEach(cleanup);

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

    await user.click(screen.getByRole("button", { name: /deactivate kitchen/i }));

    expect(screen.getByText(/deactivate kitchen\?/i)).toBeTruthy();
    expect(screen.getByRole("button", { name: /confirm deactivation/i })).toBeTruthy();
    expect(screen.getByRole("button", { name: /cancel/i })).toBeTruthy();
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
