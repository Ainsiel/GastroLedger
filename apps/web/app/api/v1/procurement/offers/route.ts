import { proxyProcurementRequest } from "@/features/procurement/procurement-proxy";

export async function GET(request: Request) {
  return proxyProcurementRequest(request, "/api/v1/procurement/offers");
}

export async function POST(request: Request) {
  return proxyProcurementRequest(request, "/api/v1/procurement/offers");
}
