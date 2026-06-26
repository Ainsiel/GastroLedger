import type { ReactNode } from "react";

import { featureId } from "@/features/platform-admin";

export default function DashboardLayout({ children }: Readonly<{ children: ReactNode }>) {
  return <section data-feature={featureId}>{children}</section>;
}
