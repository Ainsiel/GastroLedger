import type {
  ApiProblem,
  InvitationAcceptanceRequest,
  InvitationAcceptanceResponse,
} from "@gastroledger/api-contract";

export type InvitationAcceptanceOutcome =
  | { kind: "success"; tenantName: string }
  | { kind: "validation"; message: string; correlationId?: string }
  | { kind: "conflict"; message: string; correlationId?: string }
  | { kind: "unexpected"; message: string; correlationId?: string };

function invitationProblem(problem: ApiProblem): Exclude<InvitationAcceptanceOutcome, { kind: "success" }> {
  if (problem.status === 422) {
    return {
      kind: "validation",
      message: "Review the invitation token and password.",
      correlationId: problem.correlationId,
    };
  }
  if (problem.status === 404) {
    return {
      kind: "validation",
      message: "This invitation token was not found.",
      correlationId: problem.correlationId,
    };
  }
  if (problem.status === 409) {
    const message =
      problem.type === "platform.invitation_expired"
        ? "This invitation has expired."
        : problem.type === "platform.invitation_already_used"
          ? "This invitation was already used."
          : "The invitation state changed. Review it and try again.";
    return { kind: "conflict", message, correlationId: problem.correlationId };
  }
  return {
    kind: "unexpected",
    message: "The invitation could not be accepted.",
    correlationId: problem.correlationId,
  };
}

export async function submitInvitationAcceptance(
  request: InvitationAcceptanceRequest,
  fetcher: typeof fetch = fetch,
): Promise<InvitationAcceptanceOutcome> {
  try {
    const response = await fetcher("/api/v1/users/invitations/accept", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify(request),
    });
    if (response.ok) {
      const session = (await response.json()) as InvitationAcceptanceResponse;
      return { kind: "success", tenantName: session.tenantName };
    }
    return invitationProblem((await response.json()) as ApiProblem);
  } catch {
    return { kind: "unexpected", message: "The invitation could not be accepted." };
  }
}
