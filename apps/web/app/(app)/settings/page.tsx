import { OperatingScopePage } from "@/features/platform-admin";
import { loadOperatingScopeFromServer } from "@/features/platform-admin/server";

export default async function SettingsPage() {
  return <OperatingScopePage initial={await loadOperatingScopeFromServer()} />;
}
