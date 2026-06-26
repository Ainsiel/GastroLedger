import { Store } from "lucide-react";

import { PlannedSectionPage } from "@/components/layout/planned-section-page";

export default function Page() {
  return (
    <PlannedSectionPage
      title="Store operations"
      description="Waste, transfers, counts and store-level approvals are planned."
      icon={Store}
    />
  );
}
