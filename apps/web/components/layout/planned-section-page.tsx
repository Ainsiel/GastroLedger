import type { LucideIcon } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

export function PlannedSectionPage({
  title,
  description,
  icon: Icon,
}: {
  title: string;
  description: string;
  icon: LucideIcon;
}) {
  return (
    <Card>
      <CardHeader>
        <div className="flex items-start justify-between gap-3">
          <div>
            <Badge variant="outline">Planned section</Badge>
            <CardTitle className="mt-4">{title}</CardTitle>
            <CardDescription>{description}</CardDescription>
          </div>
          <div className="flex size-11 items-center justify-center rounded-lg bg-accent text-accent-foreground">
            <Icon aria-hidden="true" className="size-5" />
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <p className="max-w-3xl text-sm leading-6 text-muted-foreground">
          This navigation target is protected and reserved for its approved backlog slice.
          No operational data entry is available here yet.
        </p>
      </CardContent>
    </Card>
  );
}
