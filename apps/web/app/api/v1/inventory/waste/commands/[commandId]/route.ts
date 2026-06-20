import { proxyInventoryRequest } from "@/features/inventory-production/inventory-proxy";
export async function POST(request: Request, { params }: { params: Promise<{ commandId: string }> }) {
  const { commandId } = await params; return proxyInventoryRequest(request, `/api/v1/inventory/waste/commands/${encodeURIComponent(commandId)}`);
}
