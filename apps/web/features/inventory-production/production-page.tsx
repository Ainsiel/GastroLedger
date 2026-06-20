"use client";

import type {
  ApiProblem,
  ProductionBatchRequest,
  ProductionBatchResponse,
} from "@gastroledger/api-contract";
import { Boxes, LoaderCircle } from "lucide-react";
import { FormEvent, useState } from "react";

import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

type Result =
  | { kind: "success"; data: ProductionBatchResponse }
  | { kind: "error"; message: string; correlationId?: string };

export function ProductionPage() {
  const [pending, setPending] = useState(false);
  const [result, setResult] = useState<Result | null>(null);

  async function postBatch(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const idempotencyKey = String(form.get("idempotencyKey"));
    const request: ProductionBatchRequest = {
      batchNumber: String(form.get("batchNumber")),
      warehouseId: String(form.get("warehouseId")),
      recipeVersionId: String(form.get("recipeVersionId")),
      actualYield: String(form.get("actualYield")),
      outputLotCode: String(form.get("outputLotCode")),
      producedOn: String(form.get("producedOn")),
      varianceReason: String(form.get("varianceReason")),
    };
    setPending(true);
    setResult(null);
    try {
      const response = await fetch(
        `/api/v1/inventory/production-batches/${encodeURIComponent(idempotencyKey)}/post`,
        { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(request) },
      );
      if (response.ok) {
        setResult({ kind: "success", data: (await response.json()) as ProductionBatchResponse });
      } else {
        const problem = (await response.json()) as ApiProblem;
        setResult({
          kind: "error",
          message:
            problem.type === "inventory.insufficient_stock"
              ? "Insufficient stock. No batch or inventory movement was posted."
              : problem.status === 401 || problem.status === 403
                ? "You are not authorized to post this production batch."
                : "The production batch could not be posted. Review the entered values.",
          correlationId: problem.correlationId,
        });
      }
    } catch {
      setResult({ kind: "error", message: "The production service is unavailable." });
    } finally {
      setPending(false);
    }
  }

  return (
    <div className="min-w-0 space-y-6 overflow-hidden">
      <header className="flex min-w-0 flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
        <div className="min-w-0">
          <div className="flex items-center gap-2 text-sm font-semibold text-primary">
            <Boxes aria-hidden="true" className="size-4" />
            Inventory &amp; production
          </div>
          <h1 className="mt-2 text-3xl font-semibold tracking-tight">Production batches</h1>
          <p className="mt-2 max-w-3xl text-sm leading-6 text-muted-foreground">
            Consume available ingredient lots and create one traceable prepared lot.
          </p>
        </div>
        <Badge variant="outline">Immutable ledger</Badge>
      </header>

      {result?.kind === "error" ? (
        <Alert role="alert" className="border-red-200 bg-red-50">
          <AlertTitle>Batch not posted</AlertTitle>
          <AlertDescription>
            {result.message}{result.correlationId ? ` Reference: ${result.correlationId}` : ""}
          </AlertDescription>
        </Alert>
      ) : null}
      {result?.kind === "success" ? (
        <Alert role="status" className="border-emerald-200 bg-emerald-50">
          <AlertTitle>Batch {result.data.batchNumber} posted</AlertTitle>
          <AlertDescription>
            {result.data.actualYield} produced from {result.data.consumedQuantity} consumed.
            Prepared lot {result.data.outputLotId} is available.
          </AlertDescription>
        </Alert>
      ) : null}

      <Card className="min-w-0 overflow-hidden">
        <CardHeader>
          <CardTitle>Post production batch</CardTitle>
          <CardDescription>
            The approved recipe version and all input allocations commit in one transaction.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={postBatch} className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
            <Field id="production-key" label="Idempotency key" name="idempotencyKey" required />
            <Field id="production-number" label="Batch number" name="batchNumber" required />
            <Field id="production-warehouse" label="Warehouse ID" name="warehouseId" required />
            <Field id="production-recipe" label="Recipe version ID" name="recipeVersionId" required />
            <Field id="production-yield" label="Actual yield" name="actualYield" inputMode="decimal" required />
            <Field id="production-lot" label="Prepared lot code" name="outputLotCode" required />
            <Field id="production-date" label="Produced on" name="producedOn" type="date" required />
            <Field id="production-variance" label="Variance reason" name="varianceReason" />
            <Button type="submit" disabled={pending} className="md:col-span-2 md:justify-self-start xl:col-span-4">
              {pending ? <LoaderCircle aria-hidden="true" className="size-4 animate-spin" /> : null}
              Post production batch
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}

function Field({
  id,
  label,
  name,
  ...props
}: { id: string; label: string; name: string } & React.ComponentProps<typeof Input>) {
  return (
    <div className="space-y-2">
      <Label htmlFor={id}>{label}</Label>
      <Input id={id} name={name} {...props} />
    </div>
  );
}
