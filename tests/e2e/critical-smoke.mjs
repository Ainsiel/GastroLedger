const endpoints = [
  ["api", process.env.API_HEALTH_URL ?? "http://127.0.0.1:58000/health"],
  ["web", process.env.WEB_HEALTH_URL ?? "http://127.0.0.1:53000/api/health"],
];

for (const [service, url] of endpoints) {
  const response = await fetch(url);
  const body = await response.json();

  if (!response.ok || body.service !== service || body.status !== "ok") {
    throw new Error(`${service} critical smoke check failed`);
  }
}

console.log("Critical technical smoke checks passed.");
