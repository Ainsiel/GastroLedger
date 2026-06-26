import { proxyOperatingRequest } from "@/features/platform-admin/operating-proxy";

export async function POST(
  request: Request,
  { params }: { params: Promise<{ branchId: string }> },
) {
  const { branchId } = await params;
  return proxyOperatingRequest(request, `/api/v1/branches/${branchId}/warehouses`);
}
