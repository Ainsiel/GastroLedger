import { cookies } from "next/headers";

import { loadMenuCatalog, type MenuCatalogSnapshot } from "./menu-catalog";

const apiBaseUrl = process.env.API_BASE_URL ?? "http://api:8000";

function sessionCookieHeader(session: { value: string } | undefined): string {
  return session ? `gl_session=${session.value}` : "";
}

export async function loadMenuCatalogFromServer(): Promise<MenuCatalogSnapshot> {
  const session = (await cookies()).get("gl_session");
  const cookie = sessionCookieHeader(session);
  const serverFetch: typeof fetch = (input, init) =>
    fetch(`${apiBaseUrl}${String(input)}`, {
      ...init,
      headers: { ...init?.headers, cookie },
      cache: "no-store",
    });

  return loadMenuCatalog(serverFetch);
}
