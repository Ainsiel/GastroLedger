import { proxyOperatingRequest } from "@/features/platform-admin/operating-proxy";

export async function POST(request: Request) {
  return proxyOperatingRequest(request, "/api/v1/users/invitations/accept");
}
