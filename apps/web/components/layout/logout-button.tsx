"use client";

import { LogOut } from "lucide-react";
import { useRouter } from "next/navigation";
import { useState } from "react";

import { Button } from "@/components/ui/button";

export function LogoutButton() {
  const router = useRouter();
  const [pending, setPending] = useState(false);

  async function logout() {
    setPending(true);
    try {
      await fetch("/api/v1/session/logout", { method: "POST" });
    } finally {
      router.replace("/login");
      router.refresh();
    }
  }

  return (
    <Button type="button" variant="outline" size="sm" onClick={logout} disabled={pending}>
      <LogOut aria-hidden="true" className="size-4" />
      {pending ? "Signing out..." : "Sign out"}
    </Button>
  );
}
