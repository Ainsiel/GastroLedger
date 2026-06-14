"use client";

import type {
  ApiProblem,
  TenantRegistrationRequest,
  TenantRegistrationResponse,
} from "@gastroledger/api-contract";
import { type FormEvent, useState } from "react";

import {
  registrationMessage,
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
    const response = await fetch("/api/v1/tenants/register", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify(request),
    });
    if (response.ok) {
      const registration = (await response.json()) as TenantRegistrationResponse;
      setOutcome({ kind: "success", tenantName: registration.tenantName });
      formElement.reset();
      return;
    }
    const problem = (await response.json()) as ApiProblem;
    if (response.status === 409) {
      setOutcome({ kind: "duplicate" });
    } else if (response.status === 422) {
      setOutcome({ kind: "validation" });
    } else {
      setOutcome({ kind: "unexpected", correlationId: problem.correlationId });
    }
  }

  return (
    <main>
      <h1>Register your company</h1>
      <p>Create a local GastroLedger tenant without payments or external services.</p>
      <form onSubmit={submit} aria-describedby="registration-status">
        <label>
          Company name
          <input name="tenantName" required autoComplete="organization" />
        </label>
        <label>
          Company identifier
          <input name="tenantSlug" required pattern="[a-z0-9]+(?:-[a-z0-9]+)*" />
        </label>
        <label>
          Administrator email
          <input name="adminEmail" required type="email" autoComplete="email" />
        </label>
        <label>
          Administrator password
          <input
            name="password"
            required
            type="password"
            minLength={12}
            autoComplete="new-password"
          />
        </label>
        <fieldset>
          <legend>Optional first branch</legend>
          <label>
            Branch name
            <input name="branchName" />
          </label>
          <label>
            Branch code
            <input name="branchCode" />
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
