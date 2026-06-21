import { proxyInventoryRequest } from "@/features/inventory-production/inventory-proxy";

export async function GET(request: Request) {
  const status = new URL(request.url).searchParams.get("status") ?? "active";
  return proxyInventoryRequest(
    request,
    `/api/v1/inventory/expiry-alerts?status=${encodeURIComponent(status)}`,
  );
}
