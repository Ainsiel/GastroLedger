import type {
  ApiProblem,
  SessionLoginRequest,
  SessionLoginResponse,
} from "@gastroledger/api-contract";

export type LoginOutcome =
  | { kind: "idle" }
  | { kind: "submitting" }
  | { kind: "success"; tenantName: string }
  | { kind: "invalid" }
  | { kind: "ambiguous"; correlationId?: string }
  | { kind: "validation"; errors: ApiProblem["errors"] }
  | { kind: "unexpected"; correlationId?: string };

export function loginMessage(outcome: LoginOutcome): string {
  switch (outcome.kind) {
    case "success":
      return `Welcome back to ${outcome.tenantName}.`;
    case "invalid":
      return "The email or password is incorrect.";
    case "ambiguous":
      return "This login belongs to more than one tenant. Tenant selection is not available yet.";
    case "validation":
      return "Review the highlighted login fields.";
    case "unexpected":
      return outcome.correlationId
        ? `Login failed. Reference: ${outcome.correlationId}`
        : "Login failed unexpectedly.";
    case "submitting":
      return "Signing in...";
    default:
      return "";
  }
}

export async function submitLogin(
  request: SessionLoginRequest,
  fetcher: typeof fetch = fetch,
): Promise<LoginOutcome> {
  try {
    const response = await fetcher("/api/v1/session/login", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify(request),
    });
    if (response.ok) {
      const session = (await response.json()) as SessionLoginResponse;
      return { kind: "success", tenantName: session.tenantName };
    }
    const problem = (await response.json()) as ApiProblem;
    if (response.status === 401) return { kind: "invalid" };
    if (response.status === 409) {
      return { kind: "ambiguous", correlationId: problem.correlationId };
    }
    if (response.status === 422) return { kind: "validation", errors: problem.errors };
    return { kind: "unexpected", correlationId: problem.correlationId };
  } catch {
    return { kind: "unexpected" };
  }
}
