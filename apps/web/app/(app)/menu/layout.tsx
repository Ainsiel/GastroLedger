import type { ReactNode } from "react";

import { featureId } from "@/features/menu-engineering";

export default function MenuLayout({ children }: Readonly<{ children: ReactNode }>) {
  return <section data-feature={featureId}>{children}</section>;
}

