// @vitest-environment jsdom

import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { WorkspaceShell } from "./workspace-shell";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ replace: vi.fn(), refresh: vi.fn() }),
}));

describe("WorkspaceShell", () => {
  afterEach(cleanup);

  it("shows tenant context, navigation and logout", () => {
    render(
      <WorkspaceShell
        tenant={{
          tenantId: "tenant-1",
          actorId: "actor-1",
          tenantName: "Sabor Central",
          tenantSlug: "sabor-central",
        }}
      >
        <p>Workspace content</p>
      </WorkspaceShell>,
    );

    expect(screen.getAllByText("Sabor Central").length).toBeGreaterThan(0);
    expect(screen.getByRole("link", { name: /dashboard/i }).getAttribute("href")).toBe(
      "/dashboard",
    );
    expect(screen.getByRole("link", { name: /organization/i }).getAttribute("href")).toBe(
      "/settings",
    );
    expect(screen.getAllByRole("button", { name: /sign out/i }).length).toBeGreaterThan(0);
  });
});
