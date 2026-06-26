import type { HealthResponse } from "@gastroledger/api-contract";

export function GET(): Response {
  const body: HealthResponse = {
    service: "web",
    status: "ok",
  };

  return Response.json(body);
}

