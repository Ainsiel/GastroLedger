import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import type { TenantIdentityResponse } from "@gastroledger/api-contract";

import { loadOperatingScope, type OperatingScopeSnapshot } from "./operating-scope";

const apiBaseUrl = process.env.API_BASE_URL ?? "http://api:8000";

function sessionCookieHeader(session: { value: string } | undefined): string {
  return session ? `gl_session=${session.value}` : "";
}

export async function getCurrentTenantFromServer(): Promise<TenantIdentityResponse | null> {
  const session = (await cookies()).get("gl_session");
  if (!session) return null;
  const response = await fetch(`${apiBaseUrl}/api/v1/session/tenant`, {
    headers: { cookie: sessionCookieHeader(session) },
    cache: "no-store",
  });
  if (!response.ok) return null;
  return (await response.json()) as TenantIdentityResponse;
}

export async function requireTenantSession(): Promise<TenantIdentityResponse> {
  const tenant = await getCurrentTenantFromServer();
  if (!tenant) redirect("/login");
  return tenant;
}

export async function loadOperatingScopeFromServer(): Promise<OperatingScopeSnapshot> {
  const session = (await cookies()).get("gl_session");
  const cookie = sessionCookieHeader(session);
  const serverFetch: typeof fetch = (input, init) =>
    fetch(`${apiBaseUrl}${String(input)}`, {
      ...init,
      headers: { ...init?.headers, cookie },
      cache: "no-store",
    });

  return loadOperatingScope(serverFetch);
}
