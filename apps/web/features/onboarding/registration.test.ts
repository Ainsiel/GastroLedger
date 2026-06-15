import { describe, expect, it } from "vitest";

import { registrationMessage, submitRegistration } from "./registration";

describe("registrationMessage", () => {
  it("maps stable registration outcomes to visible messages", () => {
    expect(registrationMessage({ kind: "success", tenantName: "Sabor Central" })).toBe(
      "Sabor Central is ready. Your administrator session is active.",
    );
    expect(registrationMessage({ kind: "duplicate" })).toBe(
      "That company identifier is already registered.",
    );
    expect(registrationMessage({ kind: "validation" })).toBe(
      "Review the highlighted registration fields.",
    );
  });

  it("returns an unexpected outcome when the public proxy is unavailable", async () => {
    const outcome = await submitRegistration(
      {
        tenantName: "Sabor Central",
        tenantSlug: "sabor-central",
        adminEmail: "admin@example.com",
        password: "StrongPassword123",
      },
      async () => {
        throw new Error("offline");
      },
    );

    expect(outcome).toEqual({ kind: "unexpected" });
  });

  it("returns an unexpected outcome when the public proxy returns invalid JSON", async () => {
    const outcome = await submitRegistration(
      {
        tenantName: "Sabor Central",
        tenantSlug: "sabor-central",
        adminEmail: "admin@example.com",
        password: "StrongPassword123",
      },
      async () => new Response("not-json", { status: 500 }),
    );

    expect(outcome).toEqual({ kind: "unexpected" });
  });
});
