"use client";

import type {
  SupplierOfferRequest,
  SupplierOfferResponse,
  SupplierReceiptRequest,
  SupplierReceiptResponse,
  SupplierRequest,
  SupplierResponse,
} from "@gastroledger/api-contract";
import { ClipboardList, LoaderCircle, PackageCheck, PackagePlus, Truck } from "lucide-react";
import { type FormEvent, useEffect, useState } from "react";

import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

import {
  loadProcurementCatalog,
  procurementRequest,
  type ProcurementCatalogSnapshot,
  type ProcurementOutcome,
} from "./suppliers";

type Notice = Exclude<ProcurementOutcome, { kind: "success" }> | { kind: "success"; message: string };

export function SuppliersPage({ initial }: { initial: ProcurementCatalogSnapshot }) {
  const [snapshot, setSnapshot] = useState(initial);
  const [notice, setNotice] = useState<Notice | null>(null);
  const [pending, setPending] = useState<string | null>(null);
  const [lastReceipt, setLastReceipt] = useState<SupplierReceiptResponse | null>(null);

  useEffect(() => {
    if (notice) document.getElementById("procurement-notice")?.focus();
  }, [notice]);

  if (snapshot.kind === "unauthorized") {
    return (
      <Alert className="border-amber-200 bg-amber-50">
        <AlertTitle>Procurement access is required</AlertTitle>
        <AlertDescription>
          Sign in with a tenant administrator session before managing suppliers and offers.
        </AlertDescription>
      </Alert>
    );
  }

  if (snapshot.kind === "unexpected") {
    return (
      <Alert className="border-red-200 bg-red-50">
        <AlertTitle>Procurement is unavailable</AlertTitle>
        <AlertDescription>
          {snapshot.correlationId
            ? `Try again later. Reference: ${snapshot.correlationId}`
            : "Try again later."}
        </AlertDescription>
      </Alert>
    );
  }

  async function refresh() {
    setSnapshot(await loadProcurementCatalog());
  }

  async function mutate<T>(
    key: string,
    path: string,
    init: RequestInit,
    successMessage: string,
  ): Promise<ProcurementOutcome<T>> {
    setPending(key);
    setNotice(null);
    const outcome = await procurementRequest<T>(path, init);
    if (outcome.kind === "success") {
      await refresh();
      setNotice({ kind: "success", message: successMessage });
    } else if (outcome.kind === "unauthorized") {
      setSnapshot({ kind: "unauthorized" });
    } else {
      setNotice(outcome);
    }
    setPending(null);
    return outcome;
  }

  async function createSupplier(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const request: SupplierRequest = {
      name: String(form.get("name")),
      code: String(form.get("code")),
    };
    await mutate<SupplierResponse>(
      "supplier",
      "/api/v1/procurement/suppliers",
      { method: "POST", body: JSON.stringify(request) },
      "Supplier saved.",
    );
  }

  async function createOffer(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const effectiveUntil = String(form.get("effectiveUntil") ?? "");
    const request: SupplierOfferRequest = {
      supplierId: String(form.get("supplierId")),
      ingredientId: String(form.get("ingredientId")),
      purchaseUnitId: String(form.get("purchaseUnitId")),
      price: String(form.get("price")),
      currency: String(form.get("currency")),
      effectiveFrom: String(form.get("effectiveFrom")),
      effectiveUntil: effectiveUntil || null,
    };
    await mutate<SupplierOfferResponse>(
      "offer",
      "/api/v1/procurement/offers",
      { method: "POST", body: JSON.stringify(request) },
      "Supplier offer saved. Price history remains visible.",
    );
  }

  async function receiveDelivery(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const receiptKey = String(form.get("idempotencyKey"));
    const request: SupplierReceiptRequest = {
      orderReference: String(form.get("orderReference")),
      supplierId: String(form.get("supplierId")),
      warehouseId: String(form.get("warehouseId")),
      receivedOn: String(form.get("receivedOn")),
      lines: [
        {
          ingredientId: String(form.get("ingredientId")),
          purchaseUnitId: String(form.get("purchaseUnitId")),
          lotCode: String(form.get("lotCode")),
          orderedQuantity: String(form.get("orderedQuantity")),
          deliveredQuantity: String(form.get("deliveredQuantity")),
          unitCost: String(form.get("unitCost")),
          expiryDate: String(form.get("expiryDate")),
          temperature: String(form.get("temperature")),
          minimumTemperature: String(form.get("minimumTemperature")),
          maximumTemperature: String(form.get("maximumTemperature")),
          tolerancePercent: String(form.get("tolerancePercent")),
        },
      ],
    };
    setPending("receipt");
    setNotice(null);
    const outcome = await procurementRequest<SupplierReceiptResponse>(
      `/api/v1/procurement/supplier-receipts/${encodeURIComponent(receiptKey)}/accept`,
      { method: "POST", body: JSON.stringify(request) },
    );
    if (outcome.kind === "success") {
      setLastReceipt(outcome.data);
      setNotice({
        kind: "success",
        message:
          outcome.data.status === "accepted"
            ? "Delivery accepted and posted to inventory."
            : outcome.data.status === "partial"
              ? "Accepted quantity posted; open remainder preserved."
              : "Delivery lines rejected; no inventory was posted.",
      });
    } else if (outcome.kind === "unauthorized") {
      setSnapshot({ kind: "unauthorized" });
    } else {
      setNotice(outcome);
    }
    setPending(null);
  }

  return (
    <div className="min-w-0 space-y-6 overflow-hidden">
      <header className="flex min-w-0 flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
        <div className="min-w-0">
          <div className="flex items-center gap-2 text-sm font-semibold text-primary">
            <ClipboardList aria-hidden="true" className="size-4" />
            Procurement
          </div>
          <h1 className="mt-2 text-3xl font-semibold tracking-tight">Procurement</h1>
          <p className="mt-2 max-w-3xl break-words text-sm leading-6 text-muted-foreground">
            Manage tenant suppliers and effective-dated ingredient offers without external
            integrations, purchase orders, payments or accounting entries.
          </p>
        </div>
        <Badge variant="outline">
          {snapshot.suppliers.length} suppliers / {snapshot.offers.length} offers
        </Badge>
      </header>

      {notice ? (
        <Alert
          id="procurement-notice"
          tabIndex={-1}
          className={
            notice.kind === "success"
              ? "border-emerald-200 bg-emerald-50"
              : "border-red-200 bg-red-50"
          }
        >
          <AlertTitle>{notice.kind === "success" ? "Saved" : "Action required"}</AlertTitle>
          <AlertDescription>
            {notice.message}
            {"correlationId" in notice && notice.correlationId
              ? ` Reference: ${notice.correlationId}`
              : ""}
          </AlertDescription>
        </Alert>
      ) : null}

      <section className="grid min-w-0 gap-6 xl:grid-cols-[minmax(0,0.9fr)_minmax(0,1.1fr)]">
        <Card className="min-w-0 overflow-hidden">
          <CardHeader>
            <div className="flex items-center gap-2">
              <Truck aria-hidden="true" className="size-5 text-primary" />
              <CardTitle>Suppliers</CardTitle>
            </div>
            <CardDescription>Create local suppliers for operational purchasing evidence.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-5">
            <form onSubmit={createSupplier} className="grid gap-4 sm:grid-cols-[1fr_0.7fr_auto]">
              <div className="space-y-2">
                <Label htmlFor="supplier-name">Supplier name</Label>
                <Input id="supplier-name" name="name" required maxLength={120} />
              </div>
              <div className="space-y-2">
                <Label htmlFor="supplier-code">Supplier code</Label>
                <Input id="supplier-code" name="code" required maxLength={63} />
              </div>
              <Button type="submit" className="self-end" disabled={pending === "supplier"}>
                {pending === "supplier" ? (
                  <LoaderCircle aria-hidden="true" className="size-4 animate-spin" />
                ) : null}
                Add supplier
              </Button>
            </form>
            {snapshot.suppliers.length === 0 ? (
              <p className="rounded-md border border-dashed p-4 text-sm text-muted-foreground">
                No suppliers configured.
              </p>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full min-w-[520px] text-sm">
                  <thead className="text-left text-muted-foreground">
                    <tr>
                      <th className="py-2 pr-4 font-medium">Code</th>
                      <th className="py-2 pr-4 font-medium">Name</th>
                      <th className="py-2 pr-4 font-medium">Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {snapshot.suppliers.map((supplier) => (
                      <tr key={supplier.supplierId} className="border-t">
                        <td className="py-3 pr-4 font-medium">{supplier.code}</td>
                        <td className="py-3 pr-4">{supplier.name}</td>
                        <td className="py-3 pr-4">{supplier.status}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </CardContent>
        </Card>

        <Card className="min-w-0 overflow-hidden">
          <CardHeader>
            <div className="flex items-center gap-2">
              <PackagePlus aria-hidden="true" className="size-5 text-primary" />
              <CardTitle>Effective offers</CardTitle>
            </div>
            <CardDescription>
              Record immutable price history for a supplier, ingredient and purchase unit.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-5">
            <form onSubmit={createOffer} className="grid gap-4 md:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor="offer-supplier">Supplier ID</Label>
                <Input id="offer-supplier" name="supplierId" required />
              </div>
              <div className="space-y-2">
                <Label htmlFor="offer-ingredient">Ingredient ID</Label>
                <Input id="offer-ingredient" name="ingredientId" required />
              </div>
              <div className="space-y-2">
                <Label htmlFor="offer-unit">Purchase unit ID</Label>
                <Input id="offer-unit" name="purchaseUnitId" required />
              </div>
              <div className="space-y-2">
                <Label htmlFor="offer-price">Price</Label>
                <Input id="offer-price" name="price" inputMode="decimal" required />
              </div>
              <div className="space-y-2">
                <Label htmlFor="offer-currency">Currency</Label>
                <Input id="offer-currency" name="currency" defaultValue="USD" required maxLength={3} />
              </div>
              <div className="space-y-2">
                <Label htmlFor="offer-effective-from">Effective from</Label>
                <Input id="offer-effective-from" name="effectiveFrom" type="date" required />
              </div>
              <div className="space-y-2">
                <Label htmlFor="offer-effective-until">Effective until</Label>
                <Input id="offer-effective-until" name="effectiveUntil" type="date" />
              </div>
              <Button type="submit" className="self-end md:col-span-2" disabled={pending === "offer"}>
                {pending === "offer" ? (
                  <LoaderCircle aria-hidden="true" className="size-4 animate-spin" />
                ) : null}
                Add offer
              </Button>
            </form>
            {snapshot.offers.length === 0 ? (
              <p className="rounded-md border border-dashed p-4 text-sm text-muted-foreground">
                No offers configured.
              </p>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full min-w-[720px] text-sm">
                  <thead className="text-left text-muted-foreground">
                    <tr>
                      <th className="py-2 pr-4 font-medium">Supplier</th>
                      <th className="py-2 pr-4 font-medium">Ingredient</th>
                      <th className="py-2 pr-4 font-medium">Price</th>
                      <th className="py-2 pr-4 font-medium">Effective</th>
                    </tr>
                  </thead>
                  <tbody>
                    {snapshot.offers.map((offer) => (
                      <tr key={offer.supplierOfferId} className="border-t">
                        <td className="py-3 pr-4 font-mono text-xs">{offer.supplierId}</td>
                        <td className="py-3 pr-4 font-mono text-xs">{offer.ingredientId}</td>
                        <td className="py-3 pr-4">
                          {offer.currency} {offer.price}
                        </td>
                        <td className="py-3 pr-4">
                          {offer.effectiveFrom}
                          {offer.effectiveUntil ? ` to ${offer.effectiveUntil}` : " onward"}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </CardContent>
        </Card>
      </section>

      <Card className="min-w-0 overflow-hidden">
        <CardHeader>
          <div className="flex items-center gap-2">
            <PackageCheck aria-hidden="true" className="size-5 text-primary" />
            <CardTitle>Receive supplier delivery</CardTitle>
          </div>
          <CardDescription>
            Post accepted lots and one immutable inventory transaction against a seeded order
            reference.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-5">
          <form onSubmit={receiveDelivery} className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
            <Field id="receipt-key" label="Receipt idempotency key" name="idempotencyKey" required />
            <Field id="receipt-order" label="Order reference" name="orderReference" required />
            <Field id="receipt-supplier" label="Receipt supplier ID" name="supplierId" required />
            <Field id="receipt-warehouse" label="Warehouse ID" name="warehouseId" required />
            <Field id="receipt-ingredient" label="Receipt ingredient ID" name="ingredientId" required />
            <Field id="receipt-unit" label="Receipt purchase unit ID" name="purchaseUnitId" required />
            <Field id="receipt-lot" label="Lot code" name="lotCode" required maxLength={80} />
            <Field id="receipt-ordered" label="Ordered quantity" name="orderedQuantity" inputMode="decimal" defaultValue="5" required />
            <Field id="receipt-delivered" label="Delivered quantity" name="deliveredQuantity" inputMode="decimal" required />
            <Field id="receipt-cost" label="Unit cost" name="unitCost" inputMode="decimal" defaultValue="1" required />
            <Field id="receipt-received" label="Received on" name="receivedOn" type="date" required />
            <Field id="receipt-expiry" label="Expiry date" name="expiryDate" type="date" required />
            <Field id="receipt-temperature" label="Temperature" name="temperature" inputMode="decimal" defaultValue="4" required />
            <Field id="receipt-min-temperature" label="Minimum temperature" name="minimumTemperature" inputMode="decimal" defaultValue="1" required />
            <Field id="receipt-max-temperature" label="Maximum temperature" name="maximumTemperature" inputMode="decimal" defaultValue="6" required />
            <Field id="receipt-tolerance" label="Tolerance percent" name="tolerancePercent" inputMode="decimal" defaultValue="0" required />
            <Button type="submit" className="xl:col-span-4 xl:justify-self-start" disabled={pending === "receipt"}>
              {pending === "receipt" ? <LoaderCircle aria-hidden="true" className="size-4 animate-spin" /> : null}
              Receive delivery
            </Button>
          </form>
          {lastReceipt ? (
            <div role="status" className="rounded-md border bg-muted/30 p-4 text-sm">
              <p className="font-semibold">Receipt {lastReceipt.status}</p>
              <p className="mt-1 text-muted-foreground">
                {lastReceipt.lines[0]?.acceptedQuantity ?? "0"} accepted /{" "}
                {lastReceipt.lines[0]?.remainingQuantity ?? "0"} remaining
              </p>
            </div>
          ) : null}
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
