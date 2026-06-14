import type { ReactNode } from "react";

import { featureId } from "@/features/inventory-production";

export default function InventoryLayout({ children }: Readonly<{ children: ReactNode }>) {
  return <section data-feature={featureId}>{children}</section>;
}

