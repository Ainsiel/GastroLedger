import { proxyOperatingRequest } from "@/features/platform-admin/operating-proxy";

export async function POST(
  request: Request,
  { params }: { params: Promise<{ warehouseId: string }> },
) {
  const { warehouseId } = await params;
  return proxyOperatingRequest(request, `/api/v1/warehouses/${warehouseId}/deactivate`);
}
