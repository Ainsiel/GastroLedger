export const featureId = "onboarding" as const;

export { registrationMessage, submitRegistration } from "./registration";
export type { RegistrationOutcome } from "./registration";
export { loginMessage, submitLogin } from "./session";
export type { LoginOutcome } from "./session";

