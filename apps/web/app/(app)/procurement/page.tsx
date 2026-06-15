import { ClipboardList } from "lucide-react";

import { PlannedSectionPage } from "@/components/layout/planned-section-page";

export default function Page() {
  return (
    <PlannedSectionPage
      title="Procurement"
      description="Supplier ordering, receiving and return workflows are planned."
      icon={ClipboardList}
    />
  );
}
