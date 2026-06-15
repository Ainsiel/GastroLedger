import { proxyOperatingRequest } from "@/features/platform-admin/operating-proxy";

export async function GET(request: Request) {
  return proxyOperatingRequest(request, "/api/v1/tenant/settings");
}

export async function PATCH(request: Request) {
  return proxyOperatingRequest(request, "/api/v1/tenant/settings");
}
