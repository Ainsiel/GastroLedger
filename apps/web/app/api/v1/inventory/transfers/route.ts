import { proxyInventoryRequest } from "@/features/inventory-production/inventory-proxy";
export async function POST(request: Request) { return proxyInventoryRequest(request, "/api/v1/inventory/transfers"); }
