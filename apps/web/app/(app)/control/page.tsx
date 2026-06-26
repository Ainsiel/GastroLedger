import { ChartNoAxesCombined } from "lucide-react";

import { PlannedSectionPage } from "@/components/layout/planned-section-page";

export default function Page() {
  return (
    <PlannedSectionPage
      title="Control & insights"
      description="Variance analysis, reporting and management insights are planned."
      icon={ChartNoAxesCombined}
    />
  );
}
