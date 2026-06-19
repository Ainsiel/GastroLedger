"use client";

import type {
  ConversionFactorRequest,
  ConversionFactorResponse,
  BranchMenuMarginResponse,
  BranchMenuPriceRequest,
  IngredientRequest,
  IngredientResponse,
  MenuItemVersionRequest,
  MenuItemVersionResponse,
  SubRecipeVersionRequest,
  SubRecipeVersionResponse,
  UnitDimension,
  UnitRequest,
  UnitResponse,
} from "@gastroledger/api-contract";
import {
  Archive,
  BookOpenCheck,
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

  async function approveSubRecipe(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const request: SubRecipeVersionRequest = {
      name: String(form.get("name")),
      code: String(form.get("code")),
      version: String(form.get("version")),
      yieldQuantity: String(form.get("yieldQuantity")),
      yieldUnitId: String(form.get("yieldUnitId")),
      effectiveFrom: String(form.get("effectiveFrom")),
      components: [
        {
          componentType: "ingredient",
          componentId: String(form.get("componentId")),
          quantity: String(form.get("componentQuantity")),
          unitId: String(form.get("componentUnitId")),
        },
      ],
    };
    await mutate<SubRecipeVersionResponse>(
      "sub-recipe",
      "/api/v1/menu/recipes/sub-recipes",
      { method: "POST", body: JSON.stringify(request) },
      "Sub-recipe version approved.",
    );
  }

  async function approveMenuItem(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const request: MenuItemVersionRequest = {
      name: String(form.get("name")),
      code: String(form.get("code")),
      version: String(form.get("version")),
      yieldQuantity: String(form.get("yieldQuantity")),
      yieldUnitId: String(form.get("yieldUnitId")),
      effectiveFrom: String(form.get("effectiveFrom")),
      components: [
        {
          componentType: "sub_recipe",
          componentId: String(form.get("componentId")),
          quantity: String(form.get("componentQuantity")),
          unitId: String(form.get("componentUnitId")),
        },
      ],
    };
    await mutate<MenuItemVersionResponse>(
      "menu-item",
      "/api/v1/menu/recipes/menu-items",
      { method: "POST", body: JSON.stringify(request) },
      "Menu item version approved.",
    );
  }

  async function createBranchPrice(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const menuItemVersionId = String(form.get("menuItemVersionId"));
    const request: BranchMenuPriceRequest = {
      branchId: String(form.get("branchId")),
      price: String(form.get("price")),
      currency: String(form.get("currency")),
      effectiveFrom: String(form.get("effectiveFrom")),
    };
    await mutate<BranchMenuMarginResponse>(
      "branch-price",
      `/api/v1/menu/recipes/menu-items/${menuItemVersionId}/branch-prices`,
      { method: "POST", body: JSON.stringify(request) },
      "Branch price saved.",
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
  const activeIngredients = snapshot.ingredients.filter((ingredient) => ingredient.availableForNewUse);
  const canApproveSubRecipe = snapshot.units.length > 0 && activeIngredients.length > 0;
  const activeSubRecipes = snapshot.subRecipes.filter((recipe) => recipe.isActive);
  const canApproveMenuItem = snapshot.units.length > 0 && activeSubRecipes.length > 0;
  const canPriceMenuItem = snapshot.menuItems.length > 0;

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
          {snapshot.units.length} units / {snapshot.ingredients.length} ingredients /{" "}
          {snapshot.subRecipes.length + snapshot.menuItems.length} recipes
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

      <Card className="min-w-0 overflow-hidden">
        <CardHeader>
          <CardTitle>Sub-recipes</CardTitle>
          <CardDescription>
            Approved versions are immutable and preserve their initial theoretical cost snapshot.
          </CardDescription>
        </CardHeader>
        <CardContent className="min-w-0 space-y-5">
          {!canApproveSubRecipe ? (
            <Alert className="border-amber-200 bg-amber-50">
              <AlertTitle>Ingredients and units are required</AlertTitle>
              <AlertDescription>
                Add at least one active ingredient with current local offer cost evidence before
                approving a sub-recipe.
              </AlertDescription>
            </Alert>
          ) : null}
          <form
            onSubmit={approveSubRecipe}
            className="grid gap-4 md:grid-cols-2 xl:grid-cols-[1fr_1fr_0.8fr_0.8fr_1fr_1fr_1fr_1fr_auto] xl:items-end"
          >
            <Field id="sub-recipe-name" label="Sub-recipe name" name="name" placeholder="Tomato base" maxLength={120} required />
            <Field id="sub-recipe-code" label="Sub-recipe code" name="code" placeholder="TOMATO-BASE" maxLength={63} required />
            <Field id="sub-recipe-version" label="Version" name="version" placeholder="v1" maxLength={40} required />
            <Field id="sub-recipe-yield" label="Yield quantity" name="yieldQuantity" inputMode="decimal" placeholder="2" required />
            <UnitSelect id="sub-recipe-yield-unit" label="Yield unit" name="yieldUnitId" units={snapshot.units} />
            <IngredientSelect id="sub-recipe-component" label="Component ingredient" name="componentId" ingredients={activeIngredients} />
            <Field id="sub-recipe-component-quantity" label="Component quantity" name="componentQuantity" inputMode="decimal" placeholder="4" required />
            <UnitSelect id="sub-recipe-component-unit" label="Component unit" name="componentUnitId" units={snapshot.units} />
            <Field id="sub-recipe-effective" label="Effective from" name="effectiveFrom" type="date" required className="xl:col-start-5" />
            <Button
              type="submit"
              className="w-full xl:w-auto"
              disabled={pending === "sub-recipe" || !canApproveSubRecipe}
            >
              {pending === "sub-recipe" ? <LoaderCircle aria-hidden="true" className="size-4 animate-spin" /> : null}
              Approve sub-recipe
            </Button>
          </form>

          {snapshot.subRecipes.length === 0 ? (
            <EmptyState icon={BookOpenCheck} title="No sub-recipes approved" text="Approved sub-recipes will show version, status and preserved theoretical cost." />
          ) : (
            <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
              {snapshot.subRecipes.map((recipe) => (
                <div key={recipe.recipeVersionId} className="rounded-lg border bg-muted/30 p-4">
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <p className="font-semibold">{recipe.name}</p>
                      <p className="mt-1 text-xs uppercase text-muted-foreground">
                        {recipe.code} / {recipe.version}
                      </p>
                    </div>
                    <Badge variant={recipe.isActive ? "default" : "outline"}>
                      {recipe.isActive ? "active" : recipe.status}
                    </Badge>
                  </div>
                  <p className="mt-3 text-sm text-muted-foreground">
                    Yield: {recipe.yieldQuantity} / Cost snapshot:{" "}
                    {recipe.costSnapshot.totalCost}
                  </p>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      <Card className="min-w-0 overflow-hidden">
        <CardHeader>
          <CardTitle>Menu items and branch margins</CardTitle>
          <CardDescription>
            Approved menu-item versions preserve theoretical cost while branch prices show
            informational margin.
          </CardDescription>
        </CardHeader>
        <CardContent className="min-w-0 space-y-5">
          {!canApproveMenuItem ? (
            <Alert className="border-amber-200 bg-amber-50">
              <AlertTitle>Approved sub-recipes are required</AlertTitle>
              <AlertDescription>
                Approve at least one active sub-recipe with current cost evidence before approving a
                menu item.
              </AlertDescription>
            </Alert>
          ) : null}
          <form
            onSubmit={approveMenuItem}
            className="grid gap-4 md:grid-cols-2 xl:grid-cols-[1fr_1fr_0.8fr_0.8fr_1fr_1fr_1fr_1fr_auto] xl:items-end"
          >
            <Field id="menu-item-name" label="Menu item name" name="name" placeholder="Lunch Bowl" maxLength={120} required />
            <Field id="menu-item-code" label="Menu item code" name="code" placeholder="LUNCH-BOWL" maxLength={63} required />
            <Field id="menu-item-version" label="Menu item version" name="version" placeholder="v1" maxLength={40} required />
            <Field id="menu-item-yield" label="Menu item serving quantity" name="yieldQuantity" inputMode="decimal" placeholder="1" required />
            <UnitSelect id="menu-item-yield-unit" label="Yield unit" name="yieldUnitId" units={snapshot.units} />
            <SubRecipeSelect id="menu-item-component" label="Component sub-recipe" name="componentId" recipes={activeSubRecipes} />
            <Field id="menu-item-component-quantity" label="Menu item sub-recipe quantity" name="componentQuantity" inputMode="decimal" placeholder="1" required />
            <UnitSelect id="menu-item-component-unit" label="Component unit" name="componentUnitId" units={snapshot.units} />
            <Field id="menu-item-effective" label="Effective from" name="effectiveFrom" type="date" required className="xl:col-start-5" />
            <Button
              type="submit"
              className="w-full xl:w-auto"
              disabled={pending === "menu-item" || !canApproveMenuItem}
            >
              {pending === "menu-item" ? <LoaderCircle aria-hidden="true" className="size-4 animate-spin" /> : null}
              Approve menu item
            </Button>
          </form>

          {!canPriceMenuItem ? null : (
            <form
              onSubmit={createBranchPrice}
              className="grid gap-4 md:grid-cols-2 xl:grid-cols-[1.4fr_1fr_0.8fr_0.8fr_1fr_auto] xl:items-end"
            >
              <MenuItemSelect id="branch-price-menu-item" label="Menu item version" name="menuItemVersionId" recipes={snapshot.menuItems} />
              <Field id="branch-price-branch" label="Branch ID" name="branchId" required />
              <Field id="branch-price-price" label="Price" name="price" inputMode="decimal" placeholder="12.50" required />
              <Field id="branch-price-currency" label="Currency" name="currency" placeholder="USD" minLength={3} maxLength={3} required />
              <Field id="branch-price-effective" label="Effective from" name="effectiveFrom" type="date" required />
              <Button type="submit" className="w-full xl:w-auto" disabled={pending === "branch-price"}>
                Save price
              </Button>
            </form>
          )}

          {snapshot.menuItems.length === 0 ? (
            <EmptyState icon={BookOpenCheck} title="No menu items approved" text="Approved menu items will show theoretical cost, suggested price and branch margin." />
          ) : (
            <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
              {snapshot.menuItems.map((recipe) => (
                <div key={recipe.recipeVersionId} className="rounded-lg border bg-muted/30 p-4">
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <p className="font-semibold">{recipe.name}</p>
                      <p className="mt-1 text-xs uppercase text-muted-foreground">
                        {recipe.code} / {recipe.version}
                      </p>
                    </div>
                    <Badge variant={recipe.isActive ? "default" : "outline"}>
                      {recipe.isActive ? "active" : recipe.status}
                    </Badge>
                  </div>
                  <p className="mt-3 text-sm text-muted-foreground">
                    Theoretical cost: {recipe.costSnapshot.totalCost}
                  </p>
                  <div className="mt-3 space-y-2">
                    {recipe.branchMargins.length === 0 ? (
                      <p className="text-xs text-muted-foreground">No branch prices saved.</p>
                    ) : (
                      recipe.branchMargins.map((margin) => (
                        <p key={margin.branchPriceId} className="text-xs text-muted-foreground">
                          Branch {margin.branchId}: {margin.currency} {margin.price} / margin{" "}
                          {margin.marginPercent}%
                        </p>
                      ))
                    )}
                  </div>
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

function IngredientSelect({
  id,
  label,
  name,
  ingredients,
}: {
  id: string;
  label: string;
  name: string;
  ingredients: IngredientResponse[];
}) {
  return (
    <SelectField
      id={id}
      label={label}
      name={name}
      options={ingredients.map((ingredient) => [ingredient.ingredientId, `${ingredient.code} - ${ingredient.name}`])}
    />
  );
}

function SubRecipeSelect({
  id,
  label,
  name,
  recipes,
}: {
  id: string;
  label: string;
  name: string;
  recipes: SubRecipeVersionResponse[];
}) {
  return (
    <SelectField
      id={id}
      label={label}
      name={name}
      options={recipes.map((recipe) => [recipe.recipeId, `${recipe.code} - ${recipe.name}`])}
    />
  );
}

function MenuItemSelect({
  id,
  label,
  name,
  recipes,
}: {
  id: string;
  label: string;
  name: string;
  recipes: MenuItemVersionResponse[];
}) {
  return (
    <SelectField
      id={id}
      label={label}
      name={name}
      options={recipes.map((recipe) => [
        recipe.recipeVersionId,
        `${recipe.code} - ${recipe.version}`,
      ])}
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
