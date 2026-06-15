import { Suspense } from "react";

import { LoginPage } from "@/features/onboarding/login-page";

export default function Page() {
  return (
    <Suspense>
      <LoginPage />
    </Suspense>
  );
}
