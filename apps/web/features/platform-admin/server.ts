import { cookies } from "next/headers";

import { loadOperatingScope, type OperatingScopeSnapshot } from "./operating-scope";

const apiBaseUrl = process.env.API_BASE_URL ?? "http://api:8000";

export async function loadOperatingScopeFromServer(): Promise<OperatingScopeSnapshot> {
  const session = (await cookies()).get("gl_session");
  const cookie = session ? `gl_session=${session.value}` : "";
  const serverFetch: typeof fetch = (input, init) =>
    fetch(`${apiBaseUrl}${String(input)}`, {
      ...init,
      headers: { ...init?.headers, cookie },
      cache: "no-store",
    });

  return loadOperatingScope(serverFetch);
}
