import { proxyMenuCatalogRequest } from "@/features/menu-engineering/menu-proxy";

export async function POST(
  request: Request,
  { params }: { params: Promise<{ ingredientId: string }> },
) {
  const { ingredientId } = await params;
  return proxyMenuCatalogRequest(request, `/api/v1/menu/ingredients/${ingredientId}/archive`);
}
