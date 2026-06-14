import { describe, expect, it } from "vitest";

import { registrationMessage } from "./registration";

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
});
