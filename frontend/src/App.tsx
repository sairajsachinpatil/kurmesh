import { useQuery } from "@tanstack/react-query";

type Health = { status: string; services: Record<string, { status: string; detail?: string }> };
const apiBase = import.meta.env.VITE_API_BASE_URL ?? "/api/v1";

async function getHealth(): Promise<Health> {
  const response = await fetch(`${apiBase}/health`);
  if (!response.ok) throw new Error(`API health request failed (${response.status})`);
  return response.json() as Promise<Health>;
}

export function App() {
  const health = useQuery({ queryKey: ["health"], queryFn: getHealth, retry: false });
  return <main><p className="eyebrow">KURMESH · PHASE 1</p><h1>Maritime decision support infrastructure</h1><p>This environment is ready for future authenticated, human-reviewed operational workflows. No mission, environmental, ML, or routing data is shown in this phase.</p><section><h2>System health</h2>{health.isLoading && <p>Checking API connectivity…</p>}{health.isError && <p role="alert">API unavailable: {health.error.message}</p>}{health.data && <><p className={health.data.status === "LIVE" ? "ok" : "warn"}>{health.data.status}</p><ul>{Object.entries(health.data.services).map(([name, service]) => <li key={name}>{name}: <strong>{service.status}</strong>{service.detail ? ` — ${service.detail}` : ""}</li>)}</ul></>}</section></main>;
}
