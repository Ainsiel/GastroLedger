"use client";

import type {
  ConversionFactorRequest,
  ConversionFactorResponse,
  IngredientRequest,
  IngredientResponse,
  UnitDimension,
  UnitRequest,
  UnitResponse,
} from "@gastroledger/api-contract";
import {
  Archive,
  CheckCircle2,
  CookingPot,
  LoaderCircle,
  Scale,
  Utensils,
} from "lucide-react";
import { type FormEvent, useEffect, useRef, useState } from "react";

import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

import {
  loadMenuCatalog,
  menuCatalogRequest,
  type MenuCatalogOutcome,
  type MenuCatalogSnapshot,
} from "./menu-catalog";

type Notice = Exclude<MenuCatalogOutcome, { kind: "success" }> | { kind: "success"; message: string };

export function MenuCatalogPage({ initial }: { initial: MenuCatalogSnapshot }) {
  const [snapshot, setSnapshot] = useState(initial);
  const [notice, setNotice] = useState<Notice | null>(null);
  const [pending, setPending] = useState<string | null>(null);
  const [confirmIngredient, setConfirmIngredient] = useState<string | null>(null);
  const restoreArchiveFocus = useRef<string | null>(null);

  useEffect(() => {
    if (notice) document.getElementById("menu-catalog-notice")?.focus();
  }, [notice]);

  useEffect(() => {
    if (confirmIngredient) {
      document.getElementById(`confirm-archive-${confirmIngredient}`)?.focus();
      return;
    }
    if (restoreArchiveFocus.current) {
      document.getElementById(`archive-${restoreArchiveFocus.current}`)?.focus();
      restoreArchiveFocus.current = null;
    }
  }, [confirmIngredient, snapshot]);

  if (snapshot.kind === "unauthorized") {
    return (
      <Alert className="border-amber-200 bg-amber-50">
        <AlertTitle>Menu access is required</AlertTitle>
        <AlertDescription>
          Sign in with a menu engineer or tenant administrator session before managing units and
          ingredients.
        </AlertDescription>
      </Alert>
    );
  }

  if (snapshot.kind === "unexpected") {
    return (
      <Alert className="border-red-200 bg-red-50">
        <AlertTitle>Menu catalog is unavailable</AlertTitle>
        <AlertDescription>
          {snapshot.correlationId
            ? `Try again later. Reference: ${snapshot.correlationId}`
            : "Try again later."}
        </AlertDescription>
      </Alert>
    );
  }

  async function refresh() {
    setSnapshot(await loadMenuCatalog());
  }

  async function mutate<T>(
    key: string,
    path: string,
    init: RequestInit,
    successMessage: string,
  ): Promise<MenuCatalogOutcome<T>> {
    setPending(key);
    setNotice(null);
    const outcome = await menuCatalogRequest<T>(path, init);
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

  async function createUnit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const request: UnitRequest = {
      name: String(form.get("name")),
      code: String(form.get("code")),
      dimension: String(form.get("dimension")) as UnitDimension,
    };
    await mutate<UnitResponse>(
      "unit",
      "/api/v1/menu/units",
      { method: "POST", body: JSON.stringify(request) },
      "Unit created.",
    );
  }

  async function createConversion(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const request: ConversionFactorRequest = {
      sourceUnitId: String(form.get("sourceUnitId")),
      targetUnitId: String(form.get("targetUnitId")),
      factor: String(form.get("factor")),
      effectiveFrom: String(form.get("effectiveFrom")),
    };
    await mutate<ConversionFactorResponse>(
      "conversion",
      "/api/v1/menu/conversions",
      { method: "POST", body: JSON.stringify(request) },
      "Conversion factor saved.",
    );
  }

  async function createIngredient(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const request: IngredientRequest = {
      name: String(form.get("name")),
      code: String(form.get("code")),
      purchaseUnitId: String(form.get("purchaseUnitId")),
      consumptionUnitId: String(form.get("consumptionUnitId")),
      shelfLifeDays: Number(form.get("shelfLifeDays")),
      criticalStockQuantity: String(form.get("criticalStockQuantity")),
    };
    await mutate<IngredientResponse>(
      "ingredient",
      "/api/v1/menu/ingredients",
      { method: "POST", body: JSON.stringify(request) },
      "Ingredient created.",
    );
  }

  async function archiveIngredient(ingredient: IngredientResponse) {
    const outcome = await mutate<IngredientResponse>(
      `archive-${ingredient.ingredientId}`,
      `/api/v1/menu/ingredients/${ingredient.ingredientId}/archive`,
      { method: "POST" },
      `${ingredient.name} archived. History remains visible.`,
    );
    if (outcome.kind === "success") setConfirmIngredient(null);
  }

  function cancelArchive(ingredientId: string) {
    restoreArchiveFocus.current = ingredientId;
    setConfirmIngredient(null);
  }

  const canCreateIngredient = snapshot.units.length > 0;

  return (
    <div className="min-w-0 space-y-6 overflow-hidden">
      <header className="flex min-w-0 flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
        <div className="min-w-0">
          <div className="flex items-center gap-2 text-sm font-semibold text-primary">
            <CookingPot aria-hidden="true" className="size-4" />
            Menu Engineering
          </div>
          <h1 className="mt-2 text-3xl font-semibold tracking-tight">Menu engineering</h1>
          <p className="mt-2 max-w-3xl break-words text-sm leading-6 text-muted-foreground">
            Manage units, conversion factors and ingredient catalog records before recipes or
            supplier offers are introduced.
          </p>
        </div>
        <Badge variant="outline">
          {snapshot.units.length} units / {snapshot.ingredients.length} ingredients
        </Badge>
      </header>

      {notice ? (
        <Alert
          id="menu-catalog-notice"
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

      <section className="grid min-w-0 gap-6 xl:grid-cols-[minmax(0,1fr)_minmax(0,1fr)]">
        <Card className="min-w-0 overflow-hidden">
          <CardHeader>
            <CardTitle>Units</CardTitle>
            <CardDescription>
              Units are tenant-scoped and grouped by compatible dimensions.
            </CardDescription>
          </CardHeader>
          <CardContent className="min-w-0 space-y-5">
            <form onSubmit={createUnit} className="grid gap-4 sm:grid-cols-[1fr_1fr_1fr_auto] sm:items-end">
              <Field id="unit-name" label="Unit name" name="name" placeholder="Kilogram" maxLength={120} required />
              <Field id="unit-code" label="Unit code" name="code" placeholder="KG" maxLength={63} required />
              <SelectField
                id="unit-dimension"
                label="Dimension"
                name="dimension"
                defaultValue="mass"
                options={[
                  ["mass", "Mass"],
                  ["volume", "Volume"],
                  ["count", "Count"],
                ]}
              />
              <Button type="submit" className="w-full sm:w-auto" disabled={pending === "unit"}>
                {pending === "unit" ? <LoaderCircle aria-hidden="true" className="size-4 animate-spin" /> : null}
                Create unit
              </Button>
            </form>
            {snapshot.units.length === 0 ? (
              <EmptyState icon={Scale} title="No units configured" text="Create units before conversion factors or ingredients." />
            ) : (
              <div className="grid gap-3 md:grid-cols-2">
                {snapshot.units.map((unit) => (
                  <div key={unit.unitId} className="rounded-lg border bg-muted/30 p-4">
                    <div className="flex items-start justify-between gap-3">
                      <div>
                        <p className="font-semibold">{unit.name}</p>
                        <p className="mt-1 text-xs uppercase text-muted-foreground">
                          {unit.code} / {unit.dimension}
                        </p>
                      </div>
                      <Badge variant="secondary">{unit.conversions.length} factors</Badge>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        <Card className="min-w-0 overflow-hidden">
          <CardHeader>
            <CardTitle>Conversion factors</CardTitle>
            <CardDescription>
              Future factors are retained without replacing the current factor early.
            </CardDescription>
          </CardHeader>
          <CardContent className="min-w-0">
            {snapshot.units.length < 2 ? (
              <Alert className="mb-4 border-amber-200 bg-amber-50">
                <AlertTitle>Two compatible units are required</AlertTitle>
                <AlertDescription>
                  Add source and target units in the same dimension before saving a factor.
                </AlertDescription>
              </Alert>
            ) : null}
            <form onSubmit={createConversion} className="grid gap-4 sm:grid-cols-2 lg:grid-cols-[1fr_1fr_1fr_1fr_auto] lg:items-end">
              <UnitSelect id="conversion-source" label="Source unit" name="sourceUnitId" units={snapshot.units} />
              <UnitSelect id="conversion-target" label="Target unit" name="targetUnitId" units={snapshot.units} />
              <Field id="conversion-factor" label="Factor" name="factor" inputMode="decimal" placeholder="1000" required />
              <Field id="conversion-effective" label="Effective from" name="effectiveFrom" type="date" required />
              <Button
                type="submit"
                className="w-full lg:w-auto"
                disabled={pending === "conversion" || snapshot.units.length < 2}
              >
                Save factor
              </Button>
            </form>
          </CardContent>
        </Card>
      </section>

      <Card className="min-w-0 overflow-hidden">
        <CardHeader>
          <CardTitle>Ingredient catalog</CardTitle>
          <CardDescription>
            Archived ingredients remain visible but cannot be selected for new downstream use.
          </CardDescription>
        </CardHeader>
        <CardContent className="min-w-0 space-y-5">
          {!canCreateIngredient ? (
            <Alert className="border-amber-200 bg-amber-50">
              <AlertTitle>Units are required</AlertTitle>
              <AlertDescription>
                Create at least one unit before adding ingredients.
              </AlertDescription>
            </Alert>
          ) : null}
          <form onSubmit={createIngredient} className="grid gap-4 md:grid-cols-2 xl:grid-cols-[1fr_1fr_1fr_1fr_1fr_1fr_auto] xl:items-end">
            <Field id="ingredient-name" label="Ingredient name" name="name" placeholder="Flour" maxLength={120} required />
            <Field id="ingredient-code" label="Ingredient code" name="code" placeholder="FLOUR" maxLength={63} required />
            <UnitSelect id="ingredient-purchase-unit" label="Purchase unit" name="purchaseUnitId" units={snapshot.units} />
            <UnitSelect id="ingredient-consumption-unit" label="Consumption unit" name="consumptionUnitId" units={snapshot.units} />
            <Field id="ingredient-shelf-life" label="Shelf life days" name="shelfLifeDays" type="number" min={1} max={3650} required />
            <Field id="ingredient-critical-stock" label="Critical stock quantity" name="criticalStockQuantity" inputMode="decimal" placeholder="10" required />
            <Button
              type="submit"
              className="w-full xl:w-auto"
              disabled={pending === "ingredient" || !canCreateIngredient}
            >
              Add ingredient
            </Button>
          </form>

          {snapshot.ingredients.length === 0 ? (
            <EmptyState icon={Utensils} title="No ingredients configured" text="Ingredients become available to future supplier offers and recipes." />
          ) : (
            <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
              {snapshot.ingredients.map((ingredient) => (
                <div key={ingredient.ingredientId} className="rounded-lg border bg-muted/30 p-4">
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <p className="font-semibold">{ingredient.name}</p>
                      <p className="mt-1 text-xs uppercase text-muted-foreground">
                        {ingredient.code} / {ingredient.criticalStockQuantity}
                      </p>
                    </div>
                    <Badge variant={ingredient.status === "active" ? "default" : "outline"}>
                      {ingredient.status}
                    </Badge>
                  </div>
                  <p className="mt-3 text-sm text-muted-foreground">
                    Shelf life: {ingredient.shelfLifeDays} days
                  </p>
                  {ingredient.status === "active" ? (
                    confirmIngredient === ingredient.ingredientId ? (
                      <div className="mt-4 rounded-md border border-red-200 bg-red-50 p-3">
                        <p className="text-sm font-semibold">Archive {ingredient.name}?</p>
                        <p className="mt-1 text-xs text-muted-foreground">
                          History remains visible. New downstream use will be blocked.
                        </p>
                        <div className="mt-3 flex flex-wrap gap-2">
                          <Button
                            id={`confirm-archive-${ingredient.ingredientId}`}
                            type="button"
                            size="sm"
                            onClick={() => archiveIngredient(ingredient)}
                            disabled={pending === `archive-${ingredient.ingredientId}`}
                          >
                            Confirm archive
                          </Button>
                          <Button
                            type="button"
                            size="sm"
                            variant="outline"
                            onClick={() => cancelArchive(ingredient.ingredientId)}
                          >
                            Cancel
                          </Button>
                        </div>
                      </div>
                    ) : (
                      <Button
                        id={`archive-${ingredient.ingredientId}`}
                        type="button"
                        size="sm"
                        variant="outline"
                        className="mt-4"
                        onClick={() => setConfirmIngredient(ingredient.ingredientId)}
                      >
                        <Archive aria-hidden="true" className="size-4" />
                        Archive {ingredient.name}
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
        </CardContent>
      </Card>
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
  defaultValue?: string;
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

function UnitSelect({
  id,
  label,
  name,
  units,
}: {
  id: string;
  label: string;
  name: string;
  units: UnitResponse[];
}) {
  return (
    <SelectField
      id={id}
      label={label}
      name={name}
      options={units.map((unit) => [unit.unitId, `${unit.code} - ${unit.name}`])}
    />
  );
}

function EmptyState({
  icon: Icon,
  title,
  text,
}: {
  icon: typeof Scale;
  title: string;
  text: string;
}) {
  return (
    <div className="flex flex-col items-start gap-3 rounded-lg border border-dashed p-4">
      <Icon aria-hidden="true" className="size-6 text-muted-foreground" />
      <div>
        <p className="font-semibold">{title}</p>
        <p className="mt-1 text-sm text-muted-foreground">{text}</p>
      </div>
    </div>
  );
}
