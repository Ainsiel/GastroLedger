import type { TenantIdentityResponse } from "@gastroledger/api-contract";
import {
  Boxes,
  ChartNoAxesCombined,
  ClipboardList,
  CookingPot,
  Settings2,
  Store,
} from "lucide-react";
import Link from "next/link";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

const sections = [
  {
    title: "Organization settings",
    description: "Manage tenant defaults, branches and warehouses.",
    href: "/settings",
    icon: Settings2,
    status: "Available",
  },
  {
    title: "Menu engineering",
    description: "Manage units, conversions and the ingredient catalog.",
    href: "/menu",
    icon: CookingPot,
    status: "Available",
  },
  {
    title: "Procurement",
    description: "Supplier ordering and receiving workflows are planned.",
    href: "/procurement",
    icon: ClipboardList,
    status: "Planned",
  },
  {
    title: "Inventory & production",
    description: "Lots, stock movements and production batches are planned.",
    href: "/inventory",
    icon: Boxes,
    status: "Planned",
  },
  {
    title: "Store operations",
    description: "Waste, transfers and physical counts will appear here.",
    href: "/operations",
    icon: Store,
    status: "Planned",
  },
  {
    title: "Control & insights",
    description: "Operational variance and management reporting are planned.",
    href: "/control",
    icon: ChartNoAxesCombined,
    status: "Planned",
  },
];

export function DashboardPage({ tenant }: { tenant: TenantIdentityResponse }) {
  return (
    <div className="space-y-6">
      <section className="rounded-2xl border bg-card p-6 shadow-sm lg:p-8">
        <Badge variant="secondary">Tenant dashboard</Badge>
        <h1 className="mt-4 text-3xl font-semibold tracking-tight lg:text-4xl">
          Welcome back, {tenant.tenantName}
        </h1>
        <p className="mt-3 max-w-3xl text-sm leading-6 text-muted-foreground">
          Navigate the tenant workspace from one protected dashboard. Available
          sections are live now; planned sections remain visible so the operating
          model stays understandable while the backlog grows.
        </p>
        <div className="mt-6 flex flex-col gap-3 sm:flex-row">
          <Button asChild>
            <Link href="/settings">Open organization</Link>
          </Button>
          <Button asChild variant="outline">
            <Link href="/menu">Open menu catalog</Link>
          </Button>
        </div>
      </section>

      <section aria-labelledby="dashboard-sections" className="space-y-4">
        <div>
          <h2 id="dashboard-sections" className="text-xl font-semibold">
            Workspace sections
          </h2>
          <p className="mt-1 text-sm text-muted-foreground">
            Choose a section from the dashboard or the persistent navigation menu.
          </p>
        </div>
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {sections.map(({ title, description, href, icon: Icon, status }) => (
            <Card key={title}>
              <CardHeader>
                <div className="flex items-start justify-between gap-3">
                  <div className="flex size-10 items-center justify-center rounded-lg bg-accent text-accent-foreground">
                    <Icon aria-hidden="true" className="size-5" />
                  </div>
                  <Badge variant={status === "Available" ? "default" : "outline"}>
                    {status}
                  </Badge>
                </div>
                <CardTitle>{title}</CardTitle>
                <CardDescription>{description}</CardDescription>
              </CardHeader>
              <CardContent>
                <Button asChild variant={status === "Available" ? "default" : "outline"}>
                  <Link href={href}>
                    {status === "Available" ? "Open section" : "View planned section"}
                  </Link>
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>
      </section>
    </div>
  );
}
