// @vitest-environment jsdom

import { cleanup, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

import Page from "./page";

const replace = vi.fn();

vi.mock("next/navigation", () => ({
  useRouter: () => ({ replace }),
  useSearchParams: () => new URLSearchParams("token=prefilled-token"),
}));

describe("invitation acceptance experience", () => {
  afterEach(() => {
    cleanup();
    vi.unstubAllGlobals();
    replace.mockReset();
  });

  it("prefills the manual token and accepts the invitation into the dashboard", async () => {
    const fetcher = vi.fn().mockResolvedValue(
      Response.json({
        tenantId: "tenant-1",
        actorId: "actor-1",
        tenantName: "Sabor Central",
        tenantSlug: "sabor-central",
      }),
    );
    vi.stubGlobal("fetch", fetcher);
    const user = userEvent.setup();

    render(<Page />);

    expect(screen.getByRole("heading", { name: /accept invitation/i })).toBeTruthy();
    expect(screen.getByLabelText(/invitation token/i).getAttribute("value")).toBe(
      "prefilled-token",
    );

    await user.type(screen.getByLabelText(/password/i), "StrongPassword123");
    await user.click(screen.getByRole("button", { name: /accept invitation/i }));

    expect((await screen.findByRole("alert")).textContent).toContain("Invitation accepted");
    expect(fetcher).toHaveBeenCalledWith(
      "/api/v1/users/invitations/accept",
      expect.objectContaining({
        method: "POST",
        body: expect.stringContaining("prefilled-token"),
      }),
    );
    expect(replace).toHaveBeenCalledWith("/dashboard");
  });

  it("shows expired tokens without navigating", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        Response.json(
          {
            type: "platform.invitation_expired",
            title: "The request could not be completed",
            status: 409,
            correlationId: "expired-1",
            errors: [],
          },
          { status: 409 },
        ),
      ),
    );
    const user = userEvent.setup();

    render(<Page />);

    await user.type(screen.getByLabelText(/password/i), "StrongPassword123");
    await user.click(screen.getByRole("button", { name: /accept invitation/i }));

    expect(await screen.findByText(/this invitation has expired/i)).toBeTruthy();
    expect(replace).not.toHaveBeenCalled();
  });
});
