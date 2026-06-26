import { proxyMenuCatalogRequest } from "@/features/menu-engineering/menu-proxy";

export async function POST(
  request: Request,
  { params }: { params: Promise<{ recipeVersionId: string }> },
) {
  const { recipeVersionId } = await params;
  return proxyMenuCatalogRequest(
    request,
    `/api/v1/menu/recipes/menu-items/${recipeVersionId}/branch-prices`,
  );
}
