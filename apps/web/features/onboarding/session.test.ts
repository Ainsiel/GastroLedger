import { describe, expect, it } from "vitest";

import { loginMessage, submitLogin } from "./session";

describe("tenant session login", () => {
  it("maps a successful login to a visible welcome outcome", async () => {
    const outcome = await submitLogin(
      { email: "admin@example.com", password: "StrongPassword123" },
      async () =>
        Response.json({
          tenantId: "tenant-1",
          actorId: "actor-1",
          tenantName: "Sabor Central",
          tenantSlug: "sabor-central",
        }),
    );

    expect(outcome).toEqual({ kind: "success", tenantName: "Sabor Central" });
    expect(loginMessage(outcome)).toBe("Welcome back to Sabor Central.");
  });

  it("maps invalid and ambiguous credentials to stable outcomes", async () => {
    const invalid = await submitLogin(
      { email: "missing@example.com", password: "wrong" },
      async () =>
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
    );
    const ambiguous = await submitLogin(
      { email: "admin@example.com", password: "StrongPassword123" },
      async () =>
        Response.json(
          {
            type: "platform.login_tenant_ambiguous",
            title: "The request could not be completed",
            status: 409,
            correlationId: "ambiguous-1",
            errors: [],
          },
          { status: 409 },
        ),
    );

    expect(invalid).toEqual({ kind: "invalid" });
    expect(ambiguous).toEqual({ kind: "ambiguous", correlationId: "ambiguous-1" });
  });
});
