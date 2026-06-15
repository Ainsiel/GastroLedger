// @vitest-environment jsdom

import { cleanup, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

import RegisterPage from "./page";

describe("tenant registration experience", () => {
  afterEach(() => {
    cleanup();
    vi.unstubAllGlobals();
  });

  it("groups the workflow and exposes accessible registration controls", () => {
    render(<RegisterPage />);

    expect(screen.getByRole("heading", { name: /create your gastroledger workspace/i })).toBeTruthy();
    expect(screen.getByText(/company details/i)).toBeTruthy();
    expect(screen.getByText(/administrator access/i)).toBeTruthy();
    expect(screen.getByLabelText(/company name/i).getAttribute("autocomplete")).toBe("organization");
    expect(screen.getByLabelText(/administrator email/i).getAttribute("type")).toBe("email");
    expect(screen.getByRole("button", { name: /create workspace/i })).toBeTruthy();
  });

  it("shows a visible success state after registration", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        Response.json(
          {
            tenantId: "tenant-1",
            actorId: "actor-1",
            branchId: null,
            tenantName: "Sabor Central",
            tenantSlug: "sabor-central",
          },
          { status: 201 },
        ),
      ),
    );
    const user = userEvent.setup();
    render(<RegisterPage />);

    await user.type(screen.getByLabelText(/company name/i), "Sabor Central");
    await user.type(screen.getByLabelText(/company identifier/i), "sabor-central");
    await user.type(screen.getByLabelText(/administrator email/i), "admin@example.com");
    await user.type(screen.getByLabelText(/administrator password/i), "StrongPassword123");
    await user.click(screen.getByRole("button", { name: /create workspace/i }));

    expect(await screen.findByText(/Sabor Central is ready/i)).toBeTruthy();
  });
});
