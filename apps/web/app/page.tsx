import { ArrowRight, CheckCircle2, LockKeyhole, ScrollText, Store } from "lucide-react";
import Link from "next/link";

import { PublicHeader } from "@/components/layout/public-header";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";

const principles = [
  {
    icon: LockKeyhole,
    title: "Tenant isolation by default",
    description: "Every workspace is scoped through local sessions and PostgreSQL row security.",
  },
  {
    icon: ScrollText,
    title: "Traceable operational truth",
    description: "The product is designed around explicit states, evidence and durable records.",
  },
  {
    icon: Store,
    title: "Built for restaurant groups",
    description: "Organization, menu, procurement, inventory and store operations share one model.",
  },
];

export default function Home() {
  return (
    <div className="min-h-screen">
      <PublicHeader />
      <main>
        <section className="mx-auto grid max-w-7xl gap-12 px-5 py-16 lg:grid-cols-[1.15fr_0.85fr] lg:px-8 lg:py-24">
          <div className="flex flex-col justify-center">
            <Badge variant="secondary" className="w-fit">
              Local-first restaurant operations
            </Badge>
            <h1 className="mt-6 max-w-3xl text-4xl font-semibold tracking-[-0.04em] sm:text-5xl lg:text-6xl">
              Restaurant operations deserve trustworthy data.
            </h1>
            <p className="mt-6 max-w-2xl text-lg leading-8 text-muted-foreground">
              GastroLedger connects the operational facts behind recipes, purchasing,
              inventory and store activity while keeping every tenant isolated.
            </p>
            <div className="mt-8 flex flex-col gap-3 sm:flex-row">
              <Button asChild size="lg">
                <Link href="/register">
                  Create your workspace
                  <ArrowRight aria-hidden="true" className="size-4" />
                </Link>
              </Button>
              <Button asChild size="lg" variant="outline">
                <Link href="/login">Sign in</Link>
              </Button>
            </div>
            <p className="mt-5 text-sm text-muted-foreground">
              No payments, accounting, payroll or external integrations.
            </p>
          </div>
          <Card className="overflow-hidden border-[#ddd0c2] bg-[#2b2723] text-[#fffaf3] shadow-xl">
            <CardContent className="p-6 sm:p-8">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[#c8b9aa]">
                    Operational foundation
                  </p>
                  <p className="mt-2 text-xl font-semibold">Ready for controlled growth</p>
                </div>
                <div className="rounded-full bg-[#d77a38]/15 p-3 text-[#f0a568]">
                  <CheckCircle2 aria-hidden="true" className="size-6" />
                </div>
              </div>
              <div className="mt-8 space-y-3">
                {["Scoped company workspace", "Local administrator session", "PostgreSQL isolation evidence"].map(
                  (item) => (
                    <div key={item} className="flex items-center gap-3 rounded-lg bg-white/6 px-4 py-3">
                      <CheckCircle2 aria-hidden="true" className="size-4 text-[#f0a568]" />
                      <span className="text-sm">{item}</span>
                    </div>
                  ),
                )}
              </div>
              <div className="mt-8 rounded-lg border border-white/10 bg-black/10 p-4 text-sm leading-6 text-[#c8b9aa]">
                Capabilities appear only when their approved work is implemented and verified.
              </div>
            </CardContent>
          </Card>
        </section>
        <section id="principles" className="border-y bg-card/75">
          <div className="mx-auto grid max-w-7xl gap-5 px-5 py-12 md:grid-cols-3 lg:px-8">
            {principles.map(({ icon: Icon, title, description }) => (
              <div key={title} className="rounded-xl border bg-card p-6 shadow-sm">
                <div className="flex size-10 items-center justify-center rounded-lg bg-accent text-accent-foreground">
                  <Icon aria-hidden="true" className="size-5" />
                </div>
                <h2 className="mt-5 font-semibold">{title}</h2>
                <p className="mt-2 text-sm leading-6 text-muted-foreground">{description}</p>
              </div>
            ))}
          </div>
        </section>
      </main>
    </div>
  );
}
