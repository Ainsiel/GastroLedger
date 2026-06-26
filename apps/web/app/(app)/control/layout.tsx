import type { ReactNode } from "react";

import { featureId } from "@/features/control-insights";

export default function ControlLayout({ children }: Readonly<{ children: ReactNode }>) {
  return <section data-feature={featureId}>{children}</section>;
}

