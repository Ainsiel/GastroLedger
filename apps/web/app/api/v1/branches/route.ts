import { proxyOperatingRequest } from "@/features/platform-admin/operating-proxy";

export async function GET(request: Request) {
  return proxyOperatingRequest(request, "/api/v1/branches");
}

export async function POST(request: Request) {
  return proxyOperatingRequest(request, "/api/v1/branches");
}
