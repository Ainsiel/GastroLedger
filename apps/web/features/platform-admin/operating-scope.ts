import type {
  ApiProblem,
  BranchResponse,
  TenantSettingsResponse,
} from "@gastroledger/api-contract";

export type OperatingScopeSnapshot =
  | { kind: "ready"; settings: TenantSettingsResponse; branches: BranchResponse[] }
  | { kind: "unauthorized" }
  | { kind: "unexpected"; correlationId?: string };

export type OperatingOutcome<T = unknown> =
  | { kind: "success"; data: T }
  | { kind: "unauthorized"; message: string; correlationId?: string }
  | { kind: "validation"; message: string; correlationId?: string }
  | { kind: "conflict"; message: string; correlationId?: string }
  | { kind: "unexpected"; message: string; correlationId?: string };

function problemOutcome(problem: ApiProblem): Exclude<OperatingOutcome, { kind: "success" }> {
  if (problem.status === 401 || problem.status === 403) {
    return {
      kind: "unauthorized",
      message: "A tenant administrator session is required.",
      correlationId: problem.correlationId,
    };
  }
  if (problem.status === 422) {
    return {
      kind: "validation",
      message: "Review the highlighted operating-scope fields.",
      correlationId: problem.correlationId,
    };
  }
  if (problem.status === 409) {
    const message =
      problem.type === "platform.code_conflict"
        ? "That code is already used in this scope."
        : problem.type === "platform.branch_limit_exceeded"
          ? "The branch limit blocks creating another branch."
          : problem.type === "platform.warehouse_has_open_movements"
            ? "This warehouse still has open movements."
            : problem.type === "platform.warehouse_inactive"
              ? "This warehouse is already inactive."
              : "The operating scope changed. Review it and try again.";
    return { kind: "conflict", message, correlationId: problem.correlationId };
  }
  return {
    kind: "unexpected",
    message: "The operating scope could not be updated.",
    correlationId: problem.correlationId,
  };
}

export async function operatingRequest<T = unknown>(
  path: string,
  init: RequestInit = {},
  fetcher: typeof fetch = fetch,
): Promise<OperatingOutcome<T>> {
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
    return { kind: "unexpected", message: "The operating scope could not be updated." };
  }
}

export async function loadOperatingScope(
  fetcher: typeof fetch = fetch,
): Promise<OperatingScopeSnapshot> {
  const settings = await operatingRequest<TenantSettingsResponse>(
    "/api/v1/tenant/settings",
    { cache: "no-store" },
    fetcher,
  );
  if (settings.kind === "unauthorized") return { kind: "unauthorized" };
  if (settings.kind !== "success") {
    return { kind: "unexpected", correlationId: settings.correlationId };
  }
  const branches = await operatingRequest<BranchResponse[]>(
    "/api/v1/branches",
    { cache: "no-store" },
    fetcher,
  );
  if (branches.kind === "unauthorized") return { kind: "unauthorized" };
  if (branches.kind !== "success") {
    return { kind: "unexpected", correlationId: branches.correlationId };
  }
  return { kind: "ready", settings: settings.data, branches: branches.data };
}
