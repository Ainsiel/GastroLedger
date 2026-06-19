import type {
  ApiProblem,
  SupplierOfferResponse,
  SupplierResponse,
} from "@gastroledger/api-contract";

export type ProcurementCatalogSnapshot =
  | { kind: "ready"; suppliers: SupplierResponse[]; offers: SupplierOfferResponse[] }
  | { kind: "unauthorized" }
  | { kind: "unexpected"; correlationId?: string };

export type ProcurementOutcome<T = unknown> =
  | { kind: "success"; data: T }
  | { kind: "unauthorized"; message: string; correlationId?: string }
  | { kind: "validation"; message: string; correlationId?: string }
  | { kind: "conflict"; message: string; correlationId?: string }
  | { kind: "unexpected"; message: string; correlationId?: string };

function problemOutcome(problem: ApiProblem): Exclude<ProcurementOutcome, { kind: "success" }> {
  if (problem.status === 401 || problem.status === 403) {
    return {
      kind: "unauthorized",
      message: "A tenant administrator session is required for procurement setup.",
      correlationId: problem.correlationId,
    };
  }
  if (problem.status === 422) {
    return {
      kind: "validation",
      message: "Review the highlighted supplier or offer fields.",
      correlationId: problem.correlationId,
    };
  }
  if (problem.status === 409) {
    const message =
      problem.type === "procurement.offer_overlap"
        ? "That supplier offer overlaps an existing effective date range."
        : problem.type === "procurement.receipt_rejected"
          ? "Temperature, duplicate lot or tolerance rules rejected this delivery line."
        : "That supplier code already exists.";
    return { kind: "conflict", message, correlationId: problem.correlationId };
  }
  return {
    kind: "unexpected",
    message: "The supplier catalog could not be updated.",
    correlationId: problem.correlationId,
  };
}

export async function procurementRequest<T = unknown>(
  path: string,
  init: RequestInit = {},
  fetcher: typeof fetch = fetch,
): Promise<ProcurementOutcome<T>> {
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
    return { kind: "unexpected", message: "The supplier catalog could not be updated." };
  }
}

export async function loadProcurementCatalog(
  fetcher: typeof fetch = fetch,
): Promise<ProcurementCatalogSnapshot> {
  const suppliers = await procurementRequest<SupplierResponse[]>(
    "/api/v1/procurement/suppliers",
    { cache: "no-store" },
    fetcher,
  );
  if (suppliers.kind === "unauthorized") return { kind: "unauthorized" };
  if (suppliers.kind !== "success") {
    return { kind: "unexpected", correlationId: suppliers.correlationId };
  }

  const offers = await procurementRequest<SupplierOfferResponse[]>(
    "/api/v1/procurement/offers",
    { cache: "no-store" },
    fetcher,
  );
  if (offers.kind === "unauthorized") return { kind: "unauthorized" };
  if (offers.kind !== "success") {
    return { kind: "unexpected", correlationId: offers.correlationId };
  }

  return { kind: "ready", suppliers: suppliers.data, offers: offers.data };
}
