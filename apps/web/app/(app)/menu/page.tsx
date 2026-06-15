import { CookingPot } from "lucide-react";

import { PlannedSectionPage } from "@/components/layout/planned-section-page";

export default function Page() {
  return (
    <PlannedSectionPage
      title="Menu engineering"
      description="Recipes, menu structure and profitability workflows are planned."
      icon={CookingPot}
    />
  );
}
