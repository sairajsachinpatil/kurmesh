import { ShieldCheck } from "lucide-react";
import { Card } from "../../components/ui/Card";
import { StatusBadge } from "../../components/ui/StatusBadge";
const factors = ["Environment", "Forecast", "Routes", "Alerts"];
export function DecisionReadiness() { return <Card><div className="flex gap-3"><ShieldCheck aria-hidden="true" className="h-6 w-6 shrink-0 text-kurmesh-blue" /><div className="w-full"><h3 className="text-xl font-bold">Decision readiness</h3><p className="mt-2 text-kurmesh-muted">Decision readiness will appear when mission, environment, forecast, and routing data are available.</p><div className="mt-4 grid gap-2 sm:grid-cols-2">{factors.map((factor) => <div key={factor} className="flex items-center justify-between rounded-lg bg-kurmesh-polar px-3 py-2"><span className="text-sm font-semibold">{factor}</span><StatusBadge status="UNAVAILABLE" /></div>)}</div></div></div></Card>; }
