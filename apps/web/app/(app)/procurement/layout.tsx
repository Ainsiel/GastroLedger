import type { ReactNode } from "react";

import { featureId } from "@/features/procurement";

export default function ProcurementLayout({ children }: Readonly<{ children: ReactNode }>) {
  return <section data-feature={featureId}>{children}</section>;
}

