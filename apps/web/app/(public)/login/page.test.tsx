// @vitest-environment jsdom

import { cleanup, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

import Page from "./page";

const replace = vi.fn();

vi.mock("next/navigation", () => ({
  useRouter: () => ({ replace }),
  useSearchParams: () => new URLSearchParams(),
}));

describe("tenant login experience", () => {
  afterEach(() => {
    cleanup();
    vi.unstubAllGlobals();
    replace.mockReset();
  });

  it("renders accessible administrator login controls", () => {
    render(<Page />);

    expect(screen.getByRole("heading", { name: /sign in to gastroledger/i })).toBeTruthy();
    expect(screen.getByLabelText(/administrator email/i).getAttribute("autocomplete")).toBe("email");
    expect(screen.getByLabelText(/password/i).getAttribute("autocomplete")).toBe("current-password");
    expect(screen.getByRole("button", { name: /sign in/i })).toBeTruthy();
    expect(screen.getByRole("link", { name: /create one first/i }).getAttribute("href")).toBe(
      "/register",
    );
  });

  it("submits credentials and sends the administrator to the dashboard", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        Response.json({
          tenantId: "tenant-1",
          actorId: "actor-1",
          tenantName: "Sabor Central",
          tenantSlug: "sabor-central",
        }),
      ),
    );
    const user = userEvent.setup();
    render(<Page />);

    await user.type(screen.getByLabelText(/administrator email/i), "admin@example.com");
    await user.type(screen.getByLabelText(/password/i), "StrongPassword123");
    await user.click(screen.getByRole("button", { name: /sign in/i }));

    expect(await screen.findByText(/welcome back to sabor central/i)).toBeTruthy();
    expect(replace).toHaveBeenCalledWith("/dashboard");
  });

  it("shows invalid credentials without navigating", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        Response.json(
          {
            type: "platform.invalid_credentials",
            title: "The request could not be completed",
            status: 401,
            correlationId: "invalid-1",
            errors: [],
          },
          { status: 401 },
        ),
      ),
    );
    const user = userEvent.setup();
    render(<Page />);

    await user.type(screen.getByLabelText(/administrator email/i), "admin@example.com");
    await user.type(screen.getByLabelText(/password/i), "wrong-password");
    await user.click(screen.getByRole("button", { name: /sign in/i }));

    expect(await screen.findByText(/email or password is incorrect/i)).toBeTruthy();
    expect(replace).not.toHaveBeenCalled();
  });
});
