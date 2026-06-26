import type { ReactNode } from "react";

import { featureId } from "@/features/store-operations";

export default function OperationsLayout({ children }: Readonly<{ children: ReactNode }>) {
  return <section data-feature={featureId}>{children}</section>;
}

