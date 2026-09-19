import { useEffect, useRef, useState } from "react";
import { Map } from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";
import { ErrorState } from "../ui/ErrorState";
import { LoadingState } from "../ui/LoadingState";
import { MapControls } from "./MapControls";
import { MapLegend } from "./MapLegend";
import { antarcticView, neutralPolarStyle } from "./mapStyles";
import type { OperationalLayer } from "./types";
export function OperationalMap({ layers = [] }: { layers?: OperationalLayer[] }) { const container = useRef<HTMLDivElement>(null); const map = useRef<Map | null>(null); const [state, setState] = useState<"loading" | "ready" | "error">("loading");
  useEffect(() => { if (!container.current) return; try { const instance = new Map({ container: container.current, style: neutralPolarStyle, center: antarcticView.center, zoom: antarcticView.zoom, maxBounds: antarcticView.maxBounds, attributionControl: false }); map.current = instance; instance.on("load", () => { instance.resize(); setState("ready"); }); instance.on("error", () => setState("error")); const observer = new ResizeObserver(() => instance.resize()); observer.observe(container.current); return () => { observer.disconnect(); instance.remove(); map.current = null; }; } catch { setState("error"); } }, []);
  const reset = () => map.current?.jumpTo({ center: antarcticView.center, zoom: antarcticView.zoom });
  return <section aria-label="Operational map" className="relative min-h-[26rem] overflow-hidden rounded-card border border-kurmesh-border bg-kurmesh-polar"><div ref={container} className="absolute inset-0" />{state === "loading" && <div className="absolute inset-0 z-20 bg-kurmesh-polar/90"><LoadingState label="Preparing Antarctic map foundation" /></div>}{state === "error" && <div className="absolute inset-4 z-20"><ErrorState title="Operational map unavailable" message="The map foundation could not be initialized. No operational layers are displayed." /></div>}{state !== "error" && <><MapControls onZoomIn={() => map.current?.zoomIn()} onZoomOut={() => map.current?.zoomOut()} onReset={reset} /><MapLegend layers={layers} /><div className="absolute left-4 top-4 z-10 max-w-xs rounded-lg border border-kurmesh-border bg-white/95 p-3 text-sm text-kurmesh-muted shadow-card"><p className="font-bold text-kurmesh-text">Antarctic operational map</p><p className="mt-1">Operational layers are unavailable until validated geospatial services are connected.</p></div></>}</section>; }
