"use client";

import type {
  BranchRequest,
  BranchResponse,
  TenantSettingsRequest,
  WarehouseRequest,
  WarehouseResponse,
} from "@gastroledger/api-contract";
import { Building2, CheckCircle2, LoaderCircle, Settings2, Warehouse } from "lucide-react";
import { type FormEvent, useEffect, useRef, useState } from "react";

import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

import {
  loadOperatingScope,
  operatingRequest,
  type OperatingOutcome,
  type OperatingScopeSnapshot,
} from "./operating-scope";

type Notice = Exclude<OperatingOutcome, { kind: "success" }> | { kind: "success"; message: string };

export function OperatingScopePage({ initial }: { initial: OperatingScopeSnapshot }) {
  const [snapshot, setSnapshot] = useState(initial);
  const [notice, setNotice] = useState<Notice | null>(null);
  const [pending, setPending] = useState<string | null>(null);
  const [confirmWarehouse, setConfirmWarehouse] = useState<string | null>(null);
  const restoreWarehouseFocus = useRef<string | null>(null);

  useEffect(() => {
    if (notice) document.getElementById("operating-scope-notice")?.focus();
  }, [notice]);

  useEffect(() => {
    if (confirmWarehouse) {
      document.getElementById(`confirm-deactivate-${confirmWarehouse}`)?.focus();
      return;
    }
    if (restoreWarehouseFocus.current) {
      document.getElementById(`deactivate-${restoreWarehouseFocus.current}`)?.focus();
      restoreWarehouseFocus.current = null;
    }
  }, [confirmWarehouse, snapshot]);

  if (snapshot.kind === "unauthorized") {
    return (
      <Alert className="border-amber-200 bg-amber-50">
        <AlertTitle>Administrator session is required</AlertTitle>
        <AlertDescription>
          Sign in with a tenant administrator session before managing organization settings.
        </AlertDescription>
      </Alert>
    );
  }

  if (snapshot.kind === "unexpected") {
    return (
      <Alert className="border-red-200 bg-red-50">
        <AlertTitle>Organization settings are unavailable</AlertTitle>
        <AlertDescription>
          {snapshot.correlationId
            ? `Try again later. Reference: ${snapshot.correlationId}`
            : "Try again later."}
        </AlertDescription>
      </Alert>
    );
  }

  async function refresh() {
    setSnapshot(await loadOperatingScope());
  }

  async function mutate<T>(
    key: string,
    path: string,
    init: RequestInit,
    successMessage: string,
  ): Promise<OperatingOutcome<T>> {
    setPending(key);
    setNotice(null);
    const outcome = await operatingRequest<T>(path, init);
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

  async function updateSettings(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const request: TenantSettingsRequest = {
      locale: String(form.get("locale")),
      baseCurrency: String(form.get("baseCurrency")),
      branchLimit: Number(form.get("branchLimit")),
    };
    await mutate("settings", "/api/v1/tenant/settings", {
      method: "PATCH",
      body: JSON.stringify(request),
    }, "Organization settings saved.");
  }

  async function createBranch(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const request: BranchRequest = {
      name: String(form.get("name")),
      code: String(form.get("code")),
    };
    await mutate<BranchResponse>("branch", "/api/v1/branches", {
      method: "POST",
      body: JSON.stringify(request),
    }, "Branch created.");
  }

  async function createWarehouse(branchId: string, event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const request: WarehouseRequest = {
      name: String(form.get("name")),
      code: String(form.get("code")),
      type: String(form.get("type")) as WarehouseRequest["type"],
    };
    await mutate<WarehouseResponse>(
      `warehouse-${branchId}`,
      `/api/v1/branches/${branchId}/warehouses`,
      { method: "POST", body: JSON.stringify(request) },
      "Warehouse created.",
    );
  }

  async function deactivateWarehouse(warehouse: WarehouseResponse) {
    const outcome = await mutate<WarehouseResponse>(
      `deactivate-${warehouse.warehouseId}`,
      `/api/v1/warehouses/${warehouse.warehouseId}/deactivate`,
      { method: "POST" },
      `${warehouse.name} deactivated. Historical visibility is retained.`,
    );
    if (outcome.kind === "success") setConfirmWarehouse(null);
  }

  function cancelWarehouseDeactivation(warehouseId: string) {
    restoreWarehouseFocus.current = warehouseId;
    setConfirmWarehouse(null);
  }

  const branchCapacityReached =
    snapshot.settings.branchCount >= snapshot.settings.branchLimit;

  return (
    <div className="space-y-6">
      <header className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <div className="flex items-center gap-2 text-sm font-semibold text-primary">
            <Settings2 aria-hidden="true" className="size-4" />
            Platform &amp; organization
          </div>
          <h1 className="mt-2 text-3xl font-semibold tracking-tight">Organization settings</h1>
          <p className="mt-2 max-w-3xl text-sm leading-6 text-muted-foreground">
            Configure descriptive tenant settings and the branches and warehouses that scope
            operational work.
          </p>
        </div>
        <Badge variant="outline">
          {snapshot.settings.branchCount} / {snapshot.settings.branchLimit} branches
        </Badge>
      </header>

      {notice ? (
        <Alert
          id="operating-scope-notice"
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

      <Card>
        <CardHeader>
          <CardTitle>Tenant defaults</CardTitle>
          <CardDescription>
            Base currency is descriptive only. GastroLedger performs no currency conversion.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={updateSettings} className="grid gap-4 lg:grid-cols-[1fr_1fr_1fr_auto] lg:items-end">
            <SelectField
              id="settings-locale"
              label="Locale"
              name="locale"
              defaultValue={snapshot.settings.locale}
              options={[
                ["en", "English"],
                ["es", "Spanish"],
                ["pt-br", "Portuguese (Brazil)"],
              ]}
            />
            <SelectField
              id="settings-base-currency"
              label="Base currency"
              name="baseCurrency"
              defaultValue={snapshot.settings.baseCurrency}
              options={[
                ["CLP", "CLP"],
                ["EUR", "EUR"],
                ["USD", "USD"],
              ]}
            />
            <Field
              id="settings-branch-limit"
              label="Branch limit"
              name="branchLimit"
              type="number"
              min={1}
              max={100}
              defaultValue={snapshot.settings.branchLimit}
              required
            />
            <Button type="submit" disabled={pending === "settings"}>
              {pending === "settings" ? <LoaderCircle aria-hidden="true" className="size-4 animate-spin" /> : null}
              Save settings
            </Button>
          </form>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Create branch</CardTitle>
          <CardDescription>
            Existing branches remain visible when the limit is reduced.
          </CardDescription>
        </CardHeader>
        <CardContent>
          {branchCapacityReached ? (
            <Alert className="mb-4 border-amber-200 bg-amber-50">
              <AlertTitle>Branch capacity reached</AlertTitle>
              <AlertDescription>
                Increase the branch limit before creating another branch.
              </AlertDescription>
            </Alert>
          ) : null}
          <form onSubmit={createBranch} className="grid gap-4 sm:grid-cols-[1fr_1fr_auto] sm:items-end">
            <Field id="new-branch-name" label="Branch name" name="name" placeholder="Downtown" maxLength={120} required />
            <Field id="new-branch-code" label="Branch code" name="code" placeholder="MAIN" maxLength={63} required />
            <Button type="submit" disabled={pending === "branch" || branchCapacityReached}>
              {pending === "branch" ? <LoaderCircle aria-hidden="true" className="size-4 animate-spin" /> : null}
              Create branch
            </Button>
          </form>
        </CardContent>
      </Card>

      <section aria-labelledby="branches-title" className="space-y-4">
        <div>
          <h2 id="branches-title" className="text-xl font-semibold">Branches and warehouses</h2>
          <p className="mt-1 text-sm text-muted-foreground">
            Inactive warehouses remain visible as historical operating scope.
          </p>
        </div>
        {snapshot.branches.length === 0 ? (
          <Card>
            <CardContent className="flex flex-col items-start gap-3 pt-6">
              <Building2 aria-hidden="true" className="size-6 text-muted-foreground" />
              <div>
                <p className="font-semibold">No branches configured</p>
                <p className="mt-1 text-sm text-muted-foreground">
                  Create the first branch when its operating location is confirmed.
                </p>
              </div>
            </CardContent>
          </Card>
        ) : (
          snapshot.branches.map((branch) => (
            <Card key={branch.branchId}>
              <CardHeader className="sm:flex-row sm:items-start sm:justify-between">
                <div>
                  <CardTitle>{branch.name}</CardTitle>
                  <CardDescription>Branch code: {branch.code}</CardDescription>
                </div>
                <Badge variant="secondary">{branch.warehouses.length} warehouses</Badge>
              </CardHeader>
              <CardContent className="space-y-5">
                {branch.warehouses.length === 0 ? (
                  <p className="rounded-lg border border-dashed p-4 text-sm text-muted-foreground">
                    No warehouses configured for this branch.
                  </p>
                ) : (
                  <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
                    {branch.warehouses.map((warehouse) => (
                      <div key={warehouse.warehouseId} className="rounded-lg border bg-muted/30 p-4">
                        <div className="flex items-start justify-between gap-3">
                          <div>
                            <p className="font-semibold">{warehouse.name}</p>
                            <p className="mt-1 text-xs uppercase tracking-wide text-muted-foreground">
                              {warehouse.code} / {warehouse.type}
                            </p>
                          </div>
                          <Badge variant={warehouse.status === "active" ? "default" : "outline"}>
                            {warehouse.status}
                          </Badge>
                        </div>
                        {warehouse.status === "active" ? (
                          confirmWarehouse === warehouse.warehouseId ? (
                            <div className="mt-4 rounded-md border border-red-200 bg-red-50 p-3">
                              <p className="text-sm font-semibold">Deactivate {warehouse.name}?</p>
                              <p className="mt-1 text-xs text-muted-foreground">
                                History remains visible. New operations will be blocked.
                              </p>
                              <div className="mt-3 flex flex-wrap gap-2">
                                 <Button
                                   id={`confirm-deactivate-${warehouse.warehouseId}`}
                                   type="button"
                                  size="sm"
                                  onClick={() => deactivateWarehouse(warehouse)}
                                  disabled={pending === `deactivate-${warehouse.warehouseId}`}
                                >
                                  Confirm deactivation
                                </Button>
                                <Button
                                  type="button"
                                  size="sm"
                                  variant="outline"
                                  onClick={() => cancelWarehouseDeactivation(warehouse.warehouseId)}
                                >
                                  Cancel
                                </Button>
                              </div>
                            </div>
                          ) : (
                            <Button
                              id={`deactivate-${warehouse.warehouseId}`}
                              type="button"
                              size="sm"
                              variant="outline"
                              className="mt-4"
                              onClick={() => setConfirmWarehouse(warehouse.warehouseId)}
                            >
                              Deactivate {warehouse.name}
                            </Button>
                          )
                        ) : (
                          <div className="mt-4 flex items-center gap-2 text-xs text-muted-foreground">
                            <CheckCircle2 aria-hidden="true" className="size-4" />
                            Historical record retained
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}
                <form
                  onSubmit={(event) => createWarehouse(branch.branchId, event)}
                  className="grid gap-4 rounded-lg border border-dashed p-4 sm:grid-cols-2 lg:grid-cols-[1fr_1fr_1fr_auto] lg:items-end"
                >
                  <div className="sm:col-span-2 lg:col-span-4 flex items-center gap-2 font-semibold">
                    <Warehouse aria-hidden="true" className="size-4" />
                    Add warehouse
                  </div>
                  <Field id={`${branch.branchId}-warehouse-name`} label="Warehouse name" name="name" placeholder="Main kitchen" maxLength={120} required />
                  <Field id={`${branch.branchId}-warehouse-code`} label="Warehouse code" name="code" placeholder="KITCHEN" maxLength={63} required />
                  <SelectField
                    id={`${branch.branchId}-warehouse-type`}
                    label="Warehouse type"
                    name="type"
                    defaultValue="general"
                    options={[
                      ["kitchen", "Kitchen"],
                      ["bar", "Bar"],
                      ["general", "General"],
                    ]}
                  />
                  <Button type="submit" disabled={pending === `warehouse-${branch.branchId}`}>
                    Add warehouse
                  </Button>
                </form>
              </CardContent>
            </Card>
          ))
        )}
      </section>
    </div>
  );
}

function Field({ id, label, name, ...props }: { id: string; label: string; name: string } & React.ComponentProps<typeof Input>) {
  return (
    <div className="space-y-2">
      <Label htmlFor={id}>{label}</Label>
      <Input id={id} name={name} {...props} />
    </div>
  );
}

function SelectField({
  label,
  id,
  name,
  defaultValue,
  options,
}: {
  label: string;
  id: string;
  name: string;
  defaultValue: string;
  options: Array<[string, string]>;
}) {
  return (
    <div className="space-y-2">
      <Label htmlFor={id}>{label}</Label>
      <select
        id={id}
        name={name}
        defaultValue={defaultValue}
        className="flex h-11 w-full rounded-md border border-input bg-card px-3 py-2 text-sm shadow-sm outline-none focus-visible:ring-2 focus-visible:ring-ring"
      >
        {options.map(([value, text]) => (
          <option key={value} value={value}>{text}</option>
        ))}
      </select>
    </div>
  );
}
