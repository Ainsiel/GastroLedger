import { proxyInventoryRequest } from "@/features/inventory-production/inventory-proxy";

export async function POST(
  request: Request,
  { params }: { params: Promise<{ alertId: string }> },
) {
  const { alertId } = await params;
  return proxyInventoryRequest(
    request,
    `/api/v1/inventory/expiry-alerts/${encodeURIComponent(alertId)}/acknowledge`,
  );
}
