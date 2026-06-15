import { Boxes } from "lucide-react";

import { PlannedSectionPage } from "@/components/layout/planned-section-page";

export default function Page() {
  return (
    <PlannedSectionPage
      title="Inventory & production"
      description="Lots, movements, production batches and stock policies are planned."
      icon={Boxes}
    />
  );
}
