"use client";

import type { SessionLoginRequest } from "@gastroledger/api-contract";
import { ArrowLeft, LoaderCircle, LogIn, ShieldCheck } from "lucide-react";
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
import { loginMessage, submitLogin, type LoginOutcome } from "./session";

export function LoginPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [outcome, setOutcome] = useState<LoginOutcome>({ kind: "idle" });
  const fieldError = (field: string) =>
    outcome.kind === "validation"
      ? outcome.errors.find((error) => error.field === field)?.detail
      : undefined;

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setOutcome({ kind: "submitting" });
    const form = new FormData(event.currentTarget);
    const request: SessionLoginRequest = {
      email: String(form.get("email") ?? ""),
      password: String(form.get("password") ?? ""),
    };
    const nextOutcome = await submitLogin(request);
    setOutcome(nextOutcome);
    if (nextOutcome.kind === "success") {
      const next = searchParams.get("next");
      router.replace(next && next.startsWith("/") ? next : "/dashboard");
    }
  }

  const statusMessage = loginMessage(outcome);

  return (
    <main className="min-h-screen lg:grid lg:grid-cols-[0.95fr_1.05fr]">
      <aside className="relative hidden overflow-hidden bg-[#292520] px-10 py-12 text-[#fffaf3] lg:flex lg:flex-col">
        <Brand className="text-[#fffaf3]" />
        <div className="my-auto max-w-lg">
          <Badge className="bg-[#d77a38] text-white">Administrator access</Badge>
          <h1 className="mt-6 text-4xl font-semibold tracking-[-0.04em]">
            Continue inside your tenant workspace.
          </h1>
          <p className="mt-5 text-base leading-7 text-[#cfc3b7]">
            Sign in with the first administrator account created during registration.
            Your session remains tenant-scoped and local to this deployment.
          </p>
          <div className="mt-8 rounded-xl border border-white/10 bg-black/10 p-5">
            <div className="flex items-center gap-3">
              <ShieldCheck aria-hidden="true" className="size-5 text-[#f0a568]" />
              <p className="font-semibold">Protected administration</p>
            </div>
            <p className="mt-3 text-sm leading-6 text-[#cfc3b7]">
              Dashboard and settings routes validate the session before rendering.
            </p>
          </div>
        </div>
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
          <Card className="w-full max-w-xl shadow-lg">
            <CardHeader>
              <div className="flex size-11 items-center justify-center rounded-lg bg-accent text-accent-foreground">
                <LogIn aria-hidden="true" className="size-5" />
              </div>
              <CardTitle className="mt-3 text-2xl sm:text-3xl">Sign in to GastroLedger</CardTitle>
              <CardDescription>
                Use your administrator email and password to open the protected workspace.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={submit} aria-describedby="login-status" className="space-y-6">
                <div className="space-y-2">
                  <Label htmlFor="email">Administrator email</Label>
                  <Input
                    id="email"
                    name="email"
                    type="email"
                    autoComplete="email"
                    required
                    maxLength={254}
                    aria-invalid={Boolean(fieldError("email"))}
                    aria-describedby={fieldError("email") ? "email-detail" : undefined}
                    placeholder="admin@example.com"
                  />
                  {fieldError("email") ? (
                    <p id="email-detail" className="text-xs text-red-700">
                      {fieldError("email")}
                    </p>
                  ) : null}
                </div>
                <div className="space-y-2">
                  <Label htmlFor="password">Password</Label>
                  <Input
                    id="password"
                    name="password"
                    type="password"
                    autoComplete="current-password"
                    required
                    maxLength={128}
                    aria-invalid={Boolean(fieldError("password"))}
                    aria-describedby={fieldError("password") ? "password-detail" : undefined}
                  />
                  {fieldError("password") ? (
                    <p id="password-detail" className="text-xs text-red-700">
                      {fieldError("password")}
                    </p>
                  ) : null}
                </div>
                {statusMessage ? (
                  <Alert
                    id="login-status"
                    className={
                      outcome.kind === "success"
                        ? "border-emerald-200 bg-emerald-50"
                        : outcome.kind === "submitting"
                          ? ""
                          : "border-red-200 bg-red-50"
                    }
                  >
                    <AlertTitle>
                      {outcome.kind === "success" ? "Session started" : "Login status"}
                    </AlertTitle>
                    <AlertDescription>{statusMessage}</AlertDescription>
                  </Alert>
                ) : (
                  <p id="login-status" role="status" aria-live="polite" className="sr-only" />
                )}
                <Button type="submit" size="lg" className="w-full" disabled={outcome.kind === "submitting"}>
                  {outcome.kind === "submitting" ? (
                    <>
                      <LoaderCircle aria-hidden="true" className="size-4 animate-spin" />
                      Signing in...
                    </>
                  ) : (
                    "Sign in"
                  )}
                </Button>
              </form>
              <Separator className="my-6" />
              <p className="text-center text-sm text-muted-foreground">
                Need a tenant workspace?{" "}
                <Link href="/register" className="font-semibold text-primary underline-offset-4 hover:underline">
                  Create one first
                </Link>
              </p>
            </CardContent>
          </Card>
        </div>
      </section>
    </main>
  );
}
