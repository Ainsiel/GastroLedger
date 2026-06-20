import { proxyInventoryRequest } from "@/features/inventory-production/inventory-proxy";
export async function POST(request: Request, { params }: { params: Promise<{ transferId: string }> }) {
  const { transferId } = await params; return proxyInventoryRequest(request, `/api/v1/inventory/transfers/${encodeURIComponent(transferId)}/approve`);
}
