"use client";

import type { ApiProblem, ExpiryAlertResponse } from "@gastroledger/api-contract";
import { BellRing, LoaderCircle } from "lucide-react";
import { FormEvent, useEffect, useState } from "react";

import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

type Status = "active" | "acknowledged";

export function ExpiryAlertPanel() {
  const [status, setStatus] = useState<Status>("active");
  const [alerts, setAlerts] = useState<ExpiryAlertResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    fetch(`/api/v1/inventory/expiry-alerts?status=${status}`)
      .then(async (response) => {
        if (cancelled) return;
        if (!response.ok) {
          const problem = await response.json() as ApiProblem;
          setError(`Expiry alerts could not be loaded. Reference: ${problem.correlationId}`);
          return;
        }
        const payload = await response.json();
        if (!Array.isArray(payload)) {
          setError("Expiry alerts returned an invalid response.");
          setAlerts([]);
          return;
        }
        setAlerts(payload as ExpiryAlertResponse[]);
      })
      .catch(() => {
        if (!cancelled) setError("The expiry alert service is unavailable.");
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => { cancelled = true; };
  }, [status]);

  function changeStatus(nextStatus: Status) {
    setStatus(nextStatus);
    setAlerts([]);
    setError(null);
    setLoading(true);
  }

  async function acknowledge(event: FormEvent<HTMLFormElement>, alertId: string) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(
        `/api/v1/inventory/expiry-alerts/${encodeURIComponent(alertId)}/acknowledge`,
        {
          method: "POST",
          headers: { "content-type": "application/json" },
          body: JSON.stringify({ actionNote: String(form.get("actionNote")) }),
        },
      );
      if (!response.ok) {
        const problem = await response.json() as ApiProblem;
        setError(`Alert was not acknowledged. Reference: ${problem.correlationId}`);
      } else {
        const updated = await response.json() as ExpiryAlertResponse;
        setAlerts((current) => current.map((item) => item.alertId === alertId ? updated : item));
      }
    } catch {
      setError("The expiry alert service is unavailable.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <Card className="min-w-0 overflow-hidden">
      <CardHeader>
        <div className="flex items-center gap-2">
          <BellRing aria-hidden="true" className="size-5 text-primary" />
          <CardTitle>Expiry alerts</CardTitle>
        </div>
        <CardDescription>Review stocked lots nearing expiry and retain action evidence.</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex gap-2" role="tablist" aria-label="Expiry alert status">
          {(["active", "acknowledged"] as const).map((value) => (
            <Button key={value} type="button" role="tab" variant={status === value ? "default" : "outline"}
              aria-selected={status === value} onClick={() => changeStatus(value)} disabled={loading}>
              {value === "active" ? "Active" : "Acknowledged"}
            </Button>
          ))}
        </div>
        {error ? <Alert role="alert" className="border-red-200 bg-red-50"><AlertTitle>Alert update failed</AlertTitle><AlertDescription>{error}</AlertDescription></Alert> : null}
        {loading && alerts.length === 0 ? <div role="status" className="flex items-center gap-2 text-sm text-muted-foreground"><LoaderCircle aria-hidden="true" className="size-4 animate-spin" />Loading expiry alerts</div> : null}
        {!loading && alerts.length === 0 ? <p className="text-sm text-muted-foreground">No {status} expiry alerts.</p> : null}
        <div className="divide-y rounded-md border">
          {alerts.map((item) => (
            <div key={item.alertId} className="grid min-w-0 gap-3 p-4 lg:grid-cols-[1fr_auto] lg:items-center">
              <div className="min-w-0">
                <div className="flex flex-wrap items-center gap-2"><strong>{item.lotCode}</strong><Badge variant="outline">{item.status}</Badge></div>
                <p className="mt-1 break-words text-sm text-muted-foreground">Expires {item.expiryDate} · Warehouse {item.warehouseId}</p>
                {item.actionNote ? <p className="mt-2 text-sm">Action: {item.actionNote}</p> : null}
              </div>
              {item.status === "active" ? (
                <form onSubmit={(event) => acknowledge(event, item.alertId)} className="grid gap-2 sm:grid-cols-[minmax(0,1fr)_auto]">
                  <div className="space-y-1"><Label htmlFor={`note-${item.alertId}`}>Action note</Label><Input id={`note-${item.alertId}`} name="actionNote" required /></div>
                  <Button type="submit" disabled={loading} className="self-end">Acknowledge</Button>
                </form>
              ) : null}
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
