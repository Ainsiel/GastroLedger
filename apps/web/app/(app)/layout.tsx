import type { ReactNode } from "react";

import { WorkspaceShell } from "@/components/layout/workspace-shell";
import { requireTenantSession } from "@/features/platform-admin/server";

export default async function AppLayout({ children }: Readonly<{ children: ReactNode }>) {
  return <WorkspaceShell tenant={await requireTenantSession()}>{children}</WorkspaceShell>;
}
