import { proxyMenuCatalogRequest } from "@/features/menu-engineering/menu-proxy";

export async function POST(request: Request) {
  return proxyMenuCatalogRequest(request, "/api/v1/menu/conversions");
}
