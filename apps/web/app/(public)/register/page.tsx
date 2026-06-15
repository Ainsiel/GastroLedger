"use client";

import type { TenantRegistrationRequest } from "@gastroledger/api-contract";
import { ArrowLeft, CheckCircle2, LoaderCircle, LockKeyhole } from "lucide-react";
import Link from "next/link";
import { type FormEvent, useState } from "react";

import { Brand } from "@/components/layout/brand";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Separator } from "@/components/ui/separator";
import {
  registrationMessage,
  submitRegistration,
  type RegistrationOutcome,
} from "@/features/onboarding";

export default function RegisterPage() {
  const [outcome, setOutcome] = useState<RegistrationOutcome>({ kind: "idle" });
  const fieldError = (field: string) =>
    outcome.kind === "validation"
      ? outcome.errors.find((error) => error.field === field)?.detail
      : undefined;

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

  const statusMessage = registrationMessage(outcome);

  return (
    <main className="min-h-screen lg:grid lg:grid-cols-[0.85fr_1.15fr]">
      <aside className="relative hidden overflow-hidden bg-[#292520] px-10 py-12 text-[#fffaf3] lg:flex lg:flex-col">
        <Brand className="text-[#fffaf3]" />
        <div className="my-auto max-w-lg">
          <Badge className="bg-[#d77a38] text-white">Tenant setup</Badge>
          <h2 className="mt-6 text-4xl font-semibold tracking-[-0.04em]">
            Start with a workspace your team can trust.
          </h2>
          <p className="mt-5 text-base leading-7 text-[#cfc3b7]">
            Registration creates an isolated local company workspace, its first
            administrator and an optional first branch in one controlled transaction.
          </p>
          <div className="mt-8 space-y-4">
            {["Local session security", "Tenant isolation through PostgreSQL RLS", "No payment or external service required"].map(
              (item) => (
                <div key={item} className="flex items-center gap-3 text-sm text-[#e9dfd4]">
                  <CheckCircle2 aria-hidden="true" className="size-4 text-[#f0a568]" />
                  {item}
                </div>
              ),
            )}
          </div>
        </div>
        <p className="text-xs leading-5 text-[#9f9184]">
          GastroLedger records operational facts. It is not accounting, payroll or a payment system.
        </p>
      </aside>
      <section className="flex min-h-screen flex-col">
        <header className="flex items-center justify-between px-5 py-5 sm:px-8">
          <Brand className="lg:hidden" />
          <Button asChild variant="ghost" className="ml-auto">
            <Link href="/">
              <ArrowLeft aria-hidden="true" className="size-4" />
              Back to overview
            </Link>
          </Button>
        </header>
        <div className="flex flex-1 items-center justify-center px-5 pb-12 sm:px-8">
          <Card className="w-full max-w-2xl shadow-lg">
            <CardHeader className="pb-4">
              <div className="flex size-11 items-center justify-center rounded-lg bg-accent text-accent-foreground">
                <LockKeyhole aria-hidden="true" className="size-5" />
              </div>
              <CardTitle className="mt-3 text-2xl sm:text-3xl">
                Create your GastroLedger workspace
              </CardTitle>
              <CardDescription>
                Set up the company identity and first administrator. A branch can be added now or later.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={submit} aria-describedby="registration-status" className="space-y-7">
                <FormSection title="Company details" description="The identifier becomes the stable local workspace key.">
                  <Field
                    label="Company name"
                    name="tenantName"
                    error={fieldError("tenantName")}
                    required
                    maxLength={120}
                    autoComplete="organization"
                    placeholder="Sabor Central"
                  />
                  <Field
                    label="Company identifier"
                    name="tenantSlug"
                    error={fieldError("tenantSlug")}
                    required
                    maxLength={63}
                    pattern="[a-z0-9]+(?:-[a-z0-9]+)*"
                    placeholder="sabor-central"
                    description="Lowercase letters, numbers and hyphens."
                  />
                </FormSection>
                <Separator />
                <FormSection title="Administrator access" description="Used only for the first local administrator.">
                  <Field
                    label="Administrator email"
                    name="adminEmail"
                    error={fieldError("adminEmail")}
                    required
                    maxLength={254}
                    type="email"
                    autoComplete="email"
                    placeholder="admin@example.com"
                  />
                  <Field
                    label="Administrator password"
                    name="password"
                    error={fieldError("password")}
                    required
                    type="password"
                    minLength={12}
                    maxLength={128}
                    autoComplete="new-password"
                    description="Use at least 12 characters."
                  />
                </FormSection>
                <Separator />
                <FormSection title="Optional first branch" description="Leave both fields empty to configure branches later.">
                  <Field label="Branch name" name="branchName" error={fieldError("firstBranch.name")} maxLength={120} placeholder="Downtown" />
                  <Field label="Branch code" name="branchCode" error={fieldError("firstBranch.code")} maxLength={63} placeholder="MAIN" />
                </FormSection>
                {statusMessage ? (
                  <Alert
                    id="registration-status"
                    className={
                      outcome.kind === "success"
                        ? "border-emerald-200 bg-emerald-50"
                        : outcome.kind === "unexpected" || outcome.kind === "duplicate" || outcome.kind === "validation"
                          ? "border-red-200 bg-red-50"
                          : ""
                    }
                  >
                    <AlertTitle>
                      {outcome.kind === "success" ? "Workspace created" : "Registration status"}
                    </AlertTitle>
                    <AlertDescription>{statusMessage}</AlertDescription>
                  </Alert>
                ) : (
                  <p id="registration-status" role="status" aria-live="polite" className="sr-only" />
                )}
                <Button type="submit" size="lg" className="w-full" disabled={outcome.kind === "submitting"}>
                  {outcome.kind === "submitting" ? (
                    <>
                      <LoaderCircle aria-hidden="true" className="size-4 animate-spin" />
                      Creating workspace...
                    </>
                  ) : (
                    "Create workspace"
                  )}
                </Button>
              </form>
            </CardContent>
          </Card>
        </div>
      </section>
    </main>
  );
}

function FormSection({
  title,
  description,
  children,
}: {
  title: string;
  description: string;
  children: React.ReactNode;
}) {
  return (
    <fieldset className="space-y-4">
      <legend className="text-base font-semibold">{title}</legend>
      <p className="-mt-2 text-sm text-muted-foreground">{description}</p>
      <div className="grid gap-4 sm:grid-cols-2">{children}</div>
    </fieldset>
  );
}

function Field({
  label,
  name,
  description,
  error,
  ...props
}: {
  label: string;
  name: string;
  description?: string;
  error?: string;
} & React.ComponentProps<typeof Input>) {
  const detailId = `${name}-detail`;
  return (
    <div className="space-y-2">
      <Label htmlFor={name}>{label}</Label>
      <Input
        id={name}
        name={name}
        aria-invalid={Boolean(error)}
        aria-describedby={description || error ? detailId : undefined}
        className={error ? "border-red-400 focus-visible:ring-red-400" : undefined}
        {...props}
      />
      {description || error ? (
        <p id={detailId} className={error ? "text-xs text-red-700" : "text-xs text-muted-foreground"}>
          {error ?? description}
        </p>
      ) : null}
    </div>
  );
}
