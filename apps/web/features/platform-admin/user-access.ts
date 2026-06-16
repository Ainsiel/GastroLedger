import type {
  ApiProblem,
  BranchAccessResponse,
  InvitationAcceptanceRequest,
  InvitationAcceptanceResponse,
  InvitationRequest,
  InvitationResponse,
} from "@gastroledger/api-contract";

export type UserAccessOutcome<T = unknown> =
  | { kind: "success"; data: T }
  | { kind: "unauthorized"; message: string; correlationId?: string }
  | { kind: "validation"; message: string; correlationId?: string }
  | { kind: "conflict"; message: string; correlationId?: string }
  | { kind: "unexpected"; message: string; correlationId?: string };

function userAccessProblem(problem: ApiProblem): Exclude<UserAccessOutcome, { kind: "success" }> {
  if (problem.status === 401 || problem.status === 403) {
    return {
      kind: "unauthorized",
      message: "A tenant administrator session is required.",
      correlationId: problem.correlationId,
    };
  }
  if (problem.status === 422) {
    return {
      kind: "validation",
      message: "Review the invitation role, scope and branch.",
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
    message: "User access could not be updated.",
    correlationId: problem.correlationId,
  };
}

export async function userAccessRequest<T = unknown>(
  path: string,
  init: RequestInit = {},
  fetcher: typeof fetch = fetch,
): Promise<UserAccessOutcome<T>> {
  try {
    const response = await fetcher(path, {
      ...init,
      headers: {
        ...(init.body ? { "content-type": "application/json" } : {}),
        ...init.headers,
      },
    });
    const body = (await response.json()) as T | ApiProblem;
    if (!response.ok) return userAccessProblem(body as ApiProblem);
    return { kind: "success", data: body as T };
  } catch {
    return { kind: "unexpected", message: "User access could not be updated." };
  }
}

export function createInvitation(
  request: InvitationRequest,
): Promise<UserAccessOutcome<InvitationResponse>> {
  return userAccessRequest<InvitationResponse>("/api/v1/users/invitations", {
    method: "POST",
    body: JSON.stringify(request),
  });
}

export function acceptInvitation(
  request: InvitationAcceptanceRequest,
): Promise<UserAccessOutcome<InvitationAcceptanceResponse>> {
  return userAccessRequest<InvitationAcceptanceResponse>("/api/v1/users/invitations/accept", {
    method: "POST",
    body: JSON.stringify(request),
  });
}

export function loadBranchAccess(
  fetcher: typeof fetch = fetch,
): Promise<UserAccessOutcome<BranchAccessResponse>> {
  return userAccessRequest<BranchAccessResponse>(
    "/api/v1/users/me/branch-access",
    { cache: "no-store" },
    fetcher,
  );
}
