import type { ReactNode } from "react";

import { featureId } from "@/features/onboarding";

export default function RegisterLayout({ children }: Readonly<{ children: ReactNode }>) {
  return <section data-feature={featureId}>{children}</section>;
}

