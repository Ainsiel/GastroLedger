"use client";

import type { InvitationAcceptanceRequest } from "@gastroledger/api-contract";
import { ArrowLeft, KeyRound, LoaderCircle, UserCheck } from "lucide-react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
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
  submitInvitationAcceptance,
  type InvitationAcceptanceOutcome,
} from "@/features/onboarding/invitation";

type AcceptOutcome =
  | { kind: "idle" }
  | { kind: "submitting" }
  | InvitationAcceptanceOutcome;

function acceptMessage(outcome: AcceptOutcome): string {
  switch (outcome.kind) {
    case "success":
      return `Invitation accepted. Opening ${outcome.tenantName}.`;
    case "validation":
      return "Review the invitation token and password.";
    case "conflict":
    case "unexpected":
      return outcome.message;
    case "submitting":
      return "Accepting invitation...";
    default:
      return "";
  }
}

export function AcceptInvitationPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [outcome, setOutcome] = useState<AcceptOutcome>({ kind: "idle" });

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setOutcome({ kind: "submitting" });
    const form = new FormData(event.currentTarget);
    const request: InvitationAcceptanceRequest = {
      manualShareToken: String(form.get("manualShareToken") ?? ""),
      password: String(form.get("password") ?? ""),
    };
    const nextOutcome = await submitInvitationAcceptance(request);
    if (nextOutcome.kind === "success") {
      setOutcome(nextOutcome);
      router.replace("/dashboard");
      return;
    }
    setOutcome(nextOutcome);
  }

  const statusMessage = acceptMessage(outcome);

  return (
    <main className="min-h-screen lg:grid lg:grid-cols-[0.95fr_1.05fr]">
      <aside className="relative hidden overflow-hidden bg-[#292520] px-10 py-12 text-[#fffaf3] lg:flex lg:flex-col">
        <Brand className="text-[#fffaf3]" />
        <div className="my-auto max-w-lg">
          <Badge className="bg-[#d77a38] text-white">Manual invitation</Badge>
          <h1 className="mt-6 text-4xl font-semibold">
            Join your tenant workspace with a local invitation.
          </h1>
          <p className="mt-5 text-base leading-7 text-[#cfc3b7]">
            Paste the token shared by your administrator and set your local password.
            The token can be used once and expires automatically.
          </p>
          <div className="mt-8 rounded-xl border border-white/10 bg-black/10 p-5">
            <div className="flex items-center gap-3">
              <KeyRound aria-hidden="true" className="size-5 text-[#f0a568]" />
              <p className="font-semibold">No external identity service</p>
            </div>
            <p className="mt-3 text-sm leading-6 text-[#cfc3b7]">
              GastroLedger accepts the invitation locally and starts a tenant-scoped session.
            </p>
          </div>
        </div>
      </aside>
      <section className="flex min-h-screen flex-col">
        <header className="flex items-center justify-between px-5 py-5 sm:px-8">
          <Brand className="lg:hidden" />
          <Button asChild variant="ghost" className="ml-auto">
            <Link href="/login">
              <ArrowLeft aria-hidden="true" className="size-4" />
              Back to sign in
            </Link>
          </Button>
        </header>
        <div className="flex flex-1 items-center justify-center px-5 pb-12 sm:px-8">
          <Card className="w-full max-w-xl shadow-lg">
            <CardHeader>
              <div className="flex size-11 items-center justify-center rounded-lg bg-accent text-accent-foreground">
                <UserCheck aria-hidden="true" className="size-5" />
              </div>
              <CardTitle className="mt-3 text-2xl sm:text-3xl">Accept invitation</CardTitle>
              <CardDescription>
                Use the manual token from your administrator and choose a password.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={submit} aria-describedby="accept-invitation-status" className="space-y-6">
                <div className="space-y-2">
                  <Label htmlFor="manual-share-token">Invitation token</Label>
                  <Input
                    id="manual-share-token"
                    name="manualShareToken"
                    defaultValue={searchParams.get("token") ?? ""}
                    autoComplete="one-time-code"
                    required
                    maxLength={256}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="password">Password</Label>
                  <Input
                    id="password"
                    name="password"
                    type="password"
                    autoComplete="new-password"
                    required
                    maxLength={128}
                  />
                </div>
                {statusMessage ? (
                  <Alert
                    id="accept-invitation-status"
                    className={
                      outcome.kind === "success"
                        ? "border-emerald-200 bg-emerald-50"
                        : outcome.kind === "submitting"
                          ? ""
                          : "border-red-200 bg-red-50"
                    }
                  >
                    <AlertTitle>
                      {outcome.kind === "success" ? "Invitation accepted" : "Invitation status"}
                    </AlertTitle>
                    <AlertDescription>
                      {statusMessage}
                      {"correlationId" in outcome && outcome.correlationId
                        ? ` Reference: ${outcome.correlationId}`
                        : ""}
                    </AlertDescription>
                  </Alert>
                ) : (
                  <p id="accept-invitation-status" role="status" aria-live="polite" className="sr-only" />
                )}
                <Button type="submit" size="lg" className="w-full" disabled={outcome.kind === "submitting"}>
                  {outcome.kind === "submitting" ? (
                    <>
                      <LoaderCircle aria-hidden="true" className="size-4 animate-spin" />
                      Accepting...
                    </>
                  ) : (
                    "Accept invitation"
                  )}
                </Button>
              </form>
              <Separator className="my-6" />
              <p className="text-center text-sm text-muted-foreground">
                Already accepted?{" "}
                <Link href="/login" className="font-semibold text-primary underline-offset-4 hover:underline">
                  Sign in
                </Link>
              </p>
            </CardContent>
          </Card>
        </div>
      </section>
    </main>
  );
}
