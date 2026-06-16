import { describe, expect, it, vi } from "vitest";

import { loadBranchAccess, userAccessRequest } from "./user-access";

describe("platform user access API consumption", () => {
  it("loads branch access from the session scoped endpoint", async () => {
    const fetcher = vi.fn().mockResolvedValue(Response.json({ branchIds: ["branch-1"] }));

    const result = await loadBranchAccess(fetcher as typeof fetch);

    expect(result).toEqual({ kind: "success", data: { branchIds: ["branch-1"] } });
    expect(fetcher).toHaveBeenCalledWith(
      "/api/v1/users/me/branch-access",
      expect.objectContaining({ cache: "no-store" }),
    );
  });

  it("normalizes expired invitation conflicts into visible outcomes", async () => {
    const result = await userAccessRequest(
      "/api/v1/users/invitations/accept",
      { method: "POST", body: JSON.stringify({ manualShareToken: "old", password: "x" }) },
      async () =>
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
    );

    expect(result).toEqual({
      kind: "conflict",
      message: "This invitation has expired.",
      correlationId: "expired-1",
    });
  });
});
