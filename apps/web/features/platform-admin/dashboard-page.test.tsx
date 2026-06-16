// @vitest-environment jsdom

import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";

import { DashboardPage } from "./dashboard-page";

describe("tenant dashboard", () => {
  afterEach(cleanup);

  it("welcomes the tenant and exposes the workspace sections", () => {
    render(
      <DashboardPage
        tenant={{
          tenantId: "tenant-1",
          actorId: "actor-1",
          tenantName: "Sabor Central",
          tenantSlug: "sabor-central",
        }}
      />,
    );

    expect(screen.getByRole("heading", { name: /welcome back, sabor central/i })).toBeTruthy();
    expect(screen.getByText(/tenant dashboard/i)).toBeTruthy();
    expect(screen.getByRole("link", { name: /open organization/i }).getAttribute("href")).toBe(
      "/settings",
    );
    expect(screen.getByRole("link", { name: /open menu catalog/i }).getAttribute("href")).toBe(
      "/menu",
    );
    expect(screen.getByRole("link", { name: /open suppliers/i }).getAttribute("href")).toBe(
      "/procurement",
    );
    expect(screen.getByText(/menu engineering/i)).toBeTruthy();
    expect(screen.getByText(/effective-dated ingredient offers/i)).toBeTruthy();
    expect(screen.getByText(/control & insights/i)).toBeTruthy();
  });
});
