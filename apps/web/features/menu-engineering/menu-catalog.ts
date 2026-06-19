import type {
  ApiProblem,
  IngredientResponse,
  SubRecipeVersionResponse,
  UnitResponse,
} from "@gastroledger/api-contract";

export type MenuCatalogSnapshot =
  | {
      kind: "ready";
      units: UnitResponse[];
      ingredients: IngredientResponse[];
      subRecipes: SubRecipeVersionResponse[];
    }
  | { kind: "unauthorized" }
  | { kind: "unexpected"; correlationId?: string };

export type MenuCatalogOutcome<T = unknown> =
  | { kind: "success"; data: T }
  | { kind: "unauthorized"; message: string; correlationId?: string }
  | { kind: "validation"; message: string; correlationId?: string }
  | { kind: "conflict"; message: string; correlationId?: string }
  | { kind: "unexpected"; message: string; correlationId?: string };

function problemOutcome(problem: ApiProblem): Exclude<MenuCatalogOutcome, { kind: "success" }> {
  if (problem.status === 401 || problem.status === 403) {
    return {
      kind: "unauthorized",
      message: "A menu engineer or tenant administrator session is required.",
      correlationId: problem.correlationId,
    };
  }
  if (problem.status === 422) {
    return {
      kind: "validation",
      message: "Review the highlighted menu catalog fields.",
      correlationId: problem.correlationId,
    };
  }
  if (problem.status === 409) {
    const message =
      problem.type === "menu.conversion_unavailable"
        ? "Add a current compatible conversion factor before using that unit mapping."
        : problem.type === "menu.recipe_graph_invalid"
          ? "Recipe approval would create a cycle or exceed the approved nesting depth."
          : problem.type === "menu.recipe_missing_cost"
            ? "Add current supplier offer cost evidence before approving this recipe."
            : problem.type === "menu.recipe_version_conflict"
              ? "That recipe version is already approved and immutable."
        : problem.type === "menu.ingredient_archived"
          ? "This ingredient is already archived."
          : "That code or effective-dated factor already exists.";
    return { kind: "conflict", message, correlationId: problem.correlationId };
  }
  return {
    kind: "unexpected",
    message: "The menu catalog could not be updated.",
    correlationId: problem.correlationId,
  };
}

export async function menuCatalogRequest<T = unknown>(
  path: string,
  init: RequestInit = {},
  fetcher: typeof fetch = fetch,
): Promise<MenuCatalogOutcome<T>> {
  try {
    const response = await fetcher(path, {
      ...init,
      headers: {
        ...(init.body ? { "content-type": "application/json" } : {}),
        ...init.headers,
      },
    });
    const body = (await response.json()) as T | ApiProblem;
    if (!response.ok) return problemOutcome(body as ApiProblem);
    return { kind: "success", data: body as T };
  } catch {
    return { kind: "unexpected", message: "The menu catalog could not be updated." };
  }
}

export async function loadMenuCatalog(
  fetcher: typeof fetch = fetch,
): Promise<MenuCatalogSnapshot> {
  const units = await menuCatalogRequest<UnitResponse[]>(
    "/api/v1/menu/units",
    { cache: "no-store" },
    fetcher,
  );
  if (units.kind === "unauthorized") return { kind: "unauthorized" };
  if (units.kind !== "success") {
    return { kind: "unexpected", correlationId: units.correlationId };
  }

  const ingredients = await menuCatalogRequest<IngredientResponse[]>(
    "/api/v1/menu/ingredients",
    { cache: "no-store" },
    fetcher,
  );
  if (ingredients.kind === "unauthorized") return { kind: "unauthorized" };
  if (ingredients.kind !== "success") {
    return { kind: "unexpected", correlationId: ingredients.correlationId };
  }

  const subRecipes = await menuCatalogRequest<SubRecipeVersionResponse[]>(
    "/api/v1/menu/recipes/sub-recipes",
    { cache: "no-store" },
    fetcher,
  );
  if (subRecipes.kind === "unauthorized") return { kind: "unauthorized" };
  if (subRecipes.kind !== "success") {
    return { kind: "unexpected", correlationId: subRecipes.correlationId };
  }

  return {
    kind: "ready",
    units: units.data,
    ingredients: ingredients.data,
    subRecipes: subRecipes.data,
  };
}
