import Link from "next/link";

import { Brand } from "@/components/layout/brand";
import { Button } from "@/components/ui/button";

export function PublicHeader() {
  return (
    <header className="border-b bg-card/80 backdrop-blur">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-5 py-4 lg:px-8">
        <Brand />
        <nav aria-label="Public navigation">
          <Button asChild size="sm">
            <Link href="/register">Create workspace</Link>
          </Button>
        </nav>
      </div>
    </header>
  );
}
