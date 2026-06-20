import { proxyInventoryRequest } from "@/features/inventory-production/inventory-proxy";

export async function POST(
  request: Request,
  { params }: { params: Promise<{ batchId: string }> },
) {
  const { batchId } = await params;
  return proxyInventoryRequest(
    request,
    `/api/v1/inventory/production-batches/${encodeURIComponent(batchId)}/post`,
  );
}
