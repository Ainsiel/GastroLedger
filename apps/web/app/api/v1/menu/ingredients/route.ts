import { proxyMenuCatalogRequest } from "@/features/menu-engineering/menu-proxy";

export async function GET(request: Request) {
  return proxyMenuCatalogRequest(request, "/api/v1/menu/ingredients");
}

export async function POST(request: Request) {
  return proxyMenuCatalogRequest(request, "/api/v1/menu/ingredients");
}
