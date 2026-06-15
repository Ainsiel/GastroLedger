// @vitest-environment jsdom

import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";

import Home from "./page";

describe("GastroLedger public home", () => {
  afterEach(cleanup);

  it("presents the approved product value and a clear registration action", () => {
    render(<Home />);

    expect(
      screen.getByRole("heading", { name: /restaurant operations deserve trustworthy data/i }),
    ).toBeTruthy();
    expect(screen.getByRole("link", { name: /create your workspace/i }).getAttribute("href")).toBe(
      "/register",
    );
    expect(screen.queryByRole("link", { name: /local api docs/i })).toBeNull();
    expect(
      screen.getByText(/no payments, accounting, payroll or external integrations/i),
    ).toBeTruthy();
  });
});
