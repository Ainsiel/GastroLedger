import { proxyProcurementRequest } from "@/features/procurement/procurement-proxy";

export async function POST(
  request: Request,
  { params }: { params: Promise<{ receiptId: string }> },
) {
  const { receiptId } = await params;
  return proxyProcurementRequest(
    request,
    `/api/v1/procurement/supplier-receipts/${encodeURIComponent(receiptId)}/accept`,
  );
}
