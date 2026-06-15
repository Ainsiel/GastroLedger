"use client";

import type { TenantRegistrationRequest } from "@gastroledger/api-contract";
import { type FormEvent, useState } from "react";

import {
  registrationMessage,
  submitRegistration,
  type RegistrationOutcome,
} from "@/features/onboarding";

export default function RegisterPage() {
  const [outcome, setOutcome] = useState<RegistrationOutcome>({ kind: "idle" });

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const formElement = event.currentTarget;
    setOutcome({ kind: "submitting" });
    const form = new FormData(formElement);
    const branchName = String(form.get("branchName") ?? "").trim();
    const branchCode = String(form.get("branchCode") ?? "").trim();
    const request: TenantRegistrationRequest = {
      tenantName: String(form.get("tenantName") ?? ""),
      tenantSlug: String(form.get("tenantSlug") ?? ""),
      adminEmail: String(form.get("adminEmail") ?? ""),
      password: String(form.get("password") ?? ""),
      ...(branchName || branchCode ? { firstBranch: { name: branchName, code: branchCode } } : {}),
    };
    const nextOutcome = await submitRegistration(request);
    setOutcome(nextOutcome);
    if (nextOutcome.kind === "success") {
      formElement.reset();
    }
  }

  return (
    <main>
      <h1>Register your company</h1>
      <p>Create a local GastroLedger tenant without payments or external services.</p>
      <form onSubmit={submit} aria-describedby="registration-status">
        <label>
          Company name
          <input name="tenantName" required maxLength={120} autoComplete="organization" />
        </label>
        <label>
          Company identifier
          <input
            name="tenantSlug"
            required
            maxLength={63}
            pattern="[a-z0-9]+(?:-[a-z0-9]+)*"
          />
        </label>
        <label>
          Administrator email
          <input name="adminEmail" required maxLength={254} type="email" autoComplete="email" />
        </label>
        <label>
          Administrator password
          <input
            name="password"
            required
            type="password"
            minLength={12}
            maxLength={128}
            autoComplete="new-password"
          />
        </label>
        <fieldset>
          <legend>Optional first branch</legend>
          <label>
            Branch name
            <input name="branchName" maxLength={120} />
          </label>
          <label>
            Branch code
            <input name="branchCode" maxLength={63} />
          </label>
        </fieldset>
        <button type="submit" disabled={outcome.kind === "submitting"}>
          Register company
        </button>
      </form>
      <p id="registration-status" role="status" aria-live="polite">
        {registrationMessage(outcome)}
      </p>
    </main>
  );
}
