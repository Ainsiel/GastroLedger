export type HealthService = "web" | "api" | "worker";

export interface HealthResponse {
  service: HealthService;
  status: "ok";
}

