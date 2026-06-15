import { DashboardPage } from "@/features/platform-admin";
import { requireTenantSession } from "@/features/platform-admin/server";

export default async function Page() {
  return <DashboardPage tenant={await requireTenantSession()} />;
}
