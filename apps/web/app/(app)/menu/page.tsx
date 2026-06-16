import { MenuCatalogPage, loadMenuCatalogFromServer } from "@/features/menu-engineering";

export default async function Page() {
  return <MenuCatalogPage initial={await loadMenuCatalogFromServer()} />;
}
