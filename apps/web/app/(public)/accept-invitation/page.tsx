import { Suspense } from "react";

import { AcceptInvitationPage } from "@/features/onboarding/accept-invitation-page";

export default function Page() {
  return (
    <Suspense>
      <AcceptInvitationPage />
    </Suspense>
  );
}
