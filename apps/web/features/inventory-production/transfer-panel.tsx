"use client";

import type { ApiProblem, TransferRequest, TransferResponse } from "@gastroledger/api-contract";
import { ArrowRightLeft, LoaderCircle } from "lucide-react";
import { FormEvent, useState } from "react";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

export function TransferPanel() {
  const [pending, setPending] = useState<string | null>(null);
  const [result, setResult] = useState<TransferResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  async function send(kind: string, path: string, body: object) {
    setPending(kind); setError(null);
    const response = await fetch(path, { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(body) });
    if (response.ok) setResult(await response.json() as TransferResponse);
    else { const problem = await response.json() as ApiProblem; setError(`${problem.type.includes("insufficient") ? "Insufficient stock" : "Transfer conflict"}. Reference: ${problem.correlationId}`); }
    setPending(null);
  }
  async function request(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); const form = new FormData(event.currentTarget);
    const body: TransferRequest = {
      transferNumber: String(form.get("transferNumber")), sourceWarehouseId: String(form.get("sourceWarehouseId")),
      destinationWarehouseId: String(form.get("destinationWarehouseId")), itemType: "ingredient",
      itemId: String(form.get("itemId")), unitId: String(form.get("unitId")), requestedQuantity: String(form.get("requestedQuantity")),
    }; await send("request", "/api/v1/inventory/transfers", body);
  }
  async function action(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); const form = new FormData(event.currentTarget);
    const submitter = (event.nativeEvent as SubmitEvent).submitter as HTMLButtonElement | null;
    const kind = submitter?.value ?? "";
    const id = String(form.get("transferId")); const key = String(form.get("commandId"));
    if (kind === "approve") await send(kind, `/api/v1/inventory/transfers/${id}/approve`, { approvedQuantity: String(form.get("quantity")) });
    if (kind === "dispatch") await send(kind, `/api/v1/inventory/transfers/${id}/dispatch/${key}`, { dispatchQuantity: String(form.get("quantity")) });
    if (kind === "receive") await send(kind, `/api/v1/inventory/transfers/${id}/receive/${key}`, { receivedQuantity: String(form.get("quantity")), lossQuantity: String(form.get("lossQuantity")), lossReason: String(form.get("lossReason")) });
  }
  return <Card className="min-w-0 overflow-hidden">
    <CardHeader><div className="flex items-center gap-2"><ArrowRightLeft className="size-5 text-primary" aria-hidden="true" /><CardTitle>Stock transfers</CardTitle></div><CardDescription>Request, approve, dispatch and reconcile stock between warehouses.</CardDescription></CardHeader>
    <CardContent className="space-y-6">
      {error ? <Alert role="alert" className="border-red-200 bg-red-50"><AlertTitle>Transfer not updated</AlertTitle><AlertDescription>{error}</AlertDescription></Alert> : null}
      {result ? <Alert role="status" className="border-emerald-200 bg-emerald-50"><AlertTitle>Transfer {result.transferNumber}: {result.status}</AlertTitle><AlertDescription>{result.dispatchedQuantity} dispatched, {result.receivedQuantity} received, {result.lossQuantity} loss.</AlertDescription></Alert> : null}
      <form onSubmit={request} className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <Field id="transfer-number" label="Transfer number" name="transferNumber" required />
        <Field id="source-warehouse" label="Source warehouse ID" name="sourceWarehouseId" required />
        <Field id="destination-warehouse" label="Destination warehouse ID" name="destinationWarehouseId" required />
        <Field id="transfer-item" label="Stock item ID" name="itemId" required />
        <Field id="transfer-unit" label="Transfer unit ID" name="unitId" required />
        <Field id="requested-quantity" label="Requested quantity" name="requestedQuantity" required inputMode="decimal" />
        <Button type="submit" disabled={pending !== null}>{pending === "request" ? <LoaderCircle className="size-4 animate-spin" aria-hidden="true" /> : null}Request transfer</Button>
      </form>
      <form onSubmit={action} className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <Field id="action-transfer" label="Transfer ID" name="transferId" required />
        <Field id="action-command" label="Command key" name="commandId" />
        <Field id="action-quantity" label="Action quantity" name="quantity" required inputMode="decimal" />
        <Field id="loss-quantity" label="Transport loss quantity" name="lossQuantity" defaultValue="0" inputMode="decimal" />
        <Field id="loss-reason" label="Transport loss reason" name="lossReason" />
        <div className="flex flex-wrap gap-2 xl:col-span-4">
          <Button name="action" value="approve" variant="outline" disabled={pending !== null}>Approve</Button>
          <Button name="action" value="dispatch" variant="outline" disabled={pending !== null}>Dispatch</Button>
          <Button name="action" value="receive" disabled={pending !== null}>Receive transfer</Button>
        </div>
      </form>
    </CardContent>
  </Card>;
}
function Field({ id, label, name, ...props }: { id: string; label: string; name: string } & React.ComponentProps<typeof Input>) {
  return <div className="space-y-2"><Label htmlFor={id}>{label}</Label><Input id={id} name={name} {...props} /></div>;
}
