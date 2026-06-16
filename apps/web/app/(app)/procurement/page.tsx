import { SuppliersPage, loadProcurementCatalogFromServer } from "@/features/procurement";

export default async function Page() {
  return <SuppliersPage initial={await loadProcurementCatalogFromServer()} />;
}
