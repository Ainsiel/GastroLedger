import {
  Boxes,
  ChartNoAxesCombined,
  ClipboardList,
  CookingPot,
  LayoutDashboard,
  Settings2,
  Store,
} from "lucide-react";
import Link from "next/link";
import type { ReactNode } from "react";
import type { TenantIdentityResponse } from "@gastroledger/api-contract";

import { Brand } from "@/components/layout/brand";
import { LogoutButton } from "@/components/layout/logout-button";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";

const navigation = [
  { label: "Dashboard", href: "/dashboard", icon: LayoutDashboard, status: "Live" },
  { label: "Organization", href: "/settings", icon: Settings2, status: "Live" },
  { label: "Menu engineering", href: "/menu", icon: CookingPot, status: "Planned" },
  { label: "Procurement", href: "/procurement", icon: ClipboardList, status: "Planned" },
  { label: "Inventory & production", href: "/inventory", icon: Boxes, status: "Planned" },
  { label: "Store operations", href: "/operations", icon: Store, status: "Planned" },
  { label: "Control & insights", href: "/control", icon: ChartNoAxesCombined, status: "Planned" },
];

export function WorkspaceShell({
  children,
  tenant,
}: {
  children: ReactNode;
  tenant: TenantIdentityResponse;
}) {
  return (
    <div className="min-h-screen lg:grid lg:grid-cols-[17rem_1fr]">
      <aside className="hidden bg-[#27231f] px-4 py-6 text-[#f8f4ee] lg:block">
        <Brand className="px-2 text-[#fffaf3]" />
        <div className="mt-8 px-2">
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[#b9ada0]">
            Workspace
          </p>
          <div className="mt-3 rounded-lg bg-white/8 p-3">
            <p className="text-sm font-semibold">{tenant.tenantName}</p>
            <p className="mt-1 text-xs text-[#b9ada0]">{tenant.tenantSlug}</p>
          </div>
        </div>
        <Separator className="my-5 bg-white/12" />
        <nav aria-label="Workspace navigation" className="space-y-1">
          {navigation.map(({ label, href, icon: Icon, status }) => (
            <Link
              key={label}
              href={href}
              className="flex min-h-10 items-center gap-3 rounded-md px-3 text-sm text-[#d6ccc1] transition hover:bg-white/8 hover:text-white focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#f0a568]"
            >
              <Icon aria-hidden="true" className="size-4" />
              <span>{label}</span>
              <Badge
                variant="outline"
                className="ml-auto border-white/15 bg-transparent text-[10px] text-[#b9ada0]"
              >
                {status}
              </Badge>
            </Link>
          ))}
        </nav>
        <div className="mt-6 px-3">
          <LogoutButton />
        </div>
      </aside>
      <main className="min-w-0">
        <header className="flex min-h-16 items-center border-b bg-card px-5 lg:px-8">
          <Brand className="lg:hidden" />
          <div className="ml-auto flex items-center gap-3">
            <div className="hidden text-right text-xs text-muted-foreground sm:block">
              <p className="font-semibold text-foreground">{tenant.tenantName}</p>
              <p>{tenant.tenantSlug}</p>
            </div>
            <LogoutButton />
          </div>
        </header>
        <div className="mx-auto max-w-7xl p-5 lg:p-8">{children}</div>
      </main>
    </div>
  );
}
