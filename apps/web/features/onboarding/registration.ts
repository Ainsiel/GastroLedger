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
