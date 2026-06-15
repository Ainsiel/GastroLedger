import {
  Boxes,
  ChartNoAxesCombined,
  ClipboardList,
  CookingPot,
  Settings2,
  Store,
} from "lucide-react";
import type { ReactNode } from "react";

import { Brand } from "@/components/layout/brand";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";

const navigation = [
  { label: "Organization", icon: Settings2 },
  { label: "Menu engineering", icon: CookingPot },
  { label: "Procurement", icon: ClipboardList },
  { label: "Inventory & production", icon: Boxes },
  { label: "Store operations", icon: Store },
  { label: "Control & insights", icon: ChartNoAxesCombined },
];

export function WorkspaceShell({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-screen lg:grid lg:grid-cols-[17rem_1fr]">
      <aside className="hidden bg-[#27231f] px-4 py-6 text-[#f8f4ee] lg:block">
        <Brand className="px-2 text-[#fffaf3]" />
        <div className="mt-8 px-2">
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[#b9ada0]">
            Workspace
          </p>
          <div className="mt-3 rounded-lg bg-white/8 p-3">
            <p className="text-sm font-semibold">Current tenant</p>
            <p className="mt-1 text-xs text-[#b9ada0]">Branch context required</p>
          </div>
        </div>
        <Separator className="my-5 bg-white/12" />
        <nav aria-label="Workspace navigation" className="space-y-1">
          {navigation.map(({ label, icon: Icon }) => (
            <div
              key={label}
              className="flex min-h-10 items-center gap-3 rounded-md px-3 text-sm text-[#d6ccc1]"
            >
              <Icon aria-hidden="true" className="size-4" />
              <span>{label}</span>
              <Badge variant="outline" className="ml-auto border-white/15 bg-transparent text-[10px] text-[#b9ada0]">
                Planned
              </Badge>
            </div>
          ))}
        </nav>
      </aside>
      <main className="min-w-0">
        <header className="flex min-h-16 items-center border-b bg-card px-5 lg:px-8">
          <Brand className="lg:hidden" />
          <div className="ml-auto text-xs text-muted-foreground">Local operational workspace</div>
        </header>
        <div className="mx-auto max-w-7xl p-5 lg:p-8">{children}</div>
      </main>
    </div>
  );
}
