import type {
  ApiProblem,
  TenantRegistrationRequest,
  TenantRegistrationResponse,
} from "@gastroledger/api-contract";

export type RegistrationOutcome =
  | { kind: "idle" }
  | { kind: "submitting" }
  | { kind: "success"; tenantName: string }
  | { kind: "duplicate" }
  | { kind: "validation" }
  | { kind: "unexpected"; correlationId?: string };

export function registrationMessage(outcome: RegistrationOutcome): string {
  switch (outcome.kind) {
    case "success":
      return `${outcome.tenantName} is ready. Your administrator session is active.`;
    case "duplicate":
      return "That company identifier is already registered.";
    case "validation":
      return "Review the highlighted registration fields.";
    case "unexpected":
      return outcome.correlationId
        ? `Registration failed. Reference: ${outcome.correlationId}`
        : "Registration failed unexpectedly.";
    case "submitting":
      return "Registering your company...";
    default:
      return "";
  }
}

export async function submitRegistration(
  request: TenantRegistrationRequest,
  fetcher: typeof fetch = fetch,
): Promise<RegistrationOutcome> {
  try {
    const response = await fetcher("/api/v1/tenants/register", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify(request),
    });
    if (response.ok) {
      const registration = (await response.json()) as TenantRegistrationResponse;
      return { kind: "success", tenantName: registration.tenantName };
    }
    const problem = (await response.json()) as ApiProblem;
    if (response.status === 409) return { kind: "duplicate" };
    if (response.status === 422) return { kind: "validation" };
    return { kind: "unexpected", correlationId: problem.correlationId };
  } catch {
    return { kind: "unexpected" };
  }
}
