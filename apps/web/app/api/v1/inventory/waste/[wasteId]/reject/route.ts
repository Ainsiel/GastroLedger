import { proxyInventoryRequest } from "@/features/inventory-production/inventory-proxy";
export async function POST(request: Request, { params }: { params: Promise<{ wasteId: string }> }) {
  const { wasteId } = await params; return proxyInventoryRequest(request, `/api/v1/inventory/waste/${encodeURIComponent(wasteId)}/reject`);
}
