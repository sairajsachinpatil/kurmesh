import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import "@testing-library/jest-dom/vitest";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { MissionWorkspacePage } from "./MissionWorkspacePage";

vi.mock("../../components/map/OperationalMap", () => ({ OperationalMap: () => <div aria-label="Operational map" /> }));

const vessel = { id: "vessel-1", name: "RV Aurora", vessel_type: "Research vessel", imo_number: null, specifications: { ice_class: "PC5" } };
const mission = { id: "mission-1", name: "Weddell research mission", state: "DRAFT", vessel_id: vessel.id, departure_at: "2026-01-10T09:00:00Z" };
const response = (body: unknown, status = 200) => new Response(JSON.stringify(body), { status, headers: { "Content-Type": "application/json" } });

function renderWorkspace() {
  return render(<QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}><MissionWorkspacePage /></QueryClientProvider>);
}

function installApi({ missions = [] as typeof mission[], vessels = [] as typeof vessel[], onPostMission, onPostVessel }: { missions?: typeof mission[]; vessels?: typeof vessel[]; onPostMission?: () => Response; onPostVessel?: () => Response } = {}) {
  vi.stubGlobal("fetch", vi.fn((input: string, init?: RequestInit) => {
    if (input.endsWith("/missions") && init?.method === "POST") return Promise.resolve(onPostMission?.() ?? response(mission, 201));
    if (input.endsWith("/vessels") && init?.method === "POST") return Promise.resolve(onPostVessel?.() ?? response(vessel, 201));
    if (input.endsWith("/missions")) return Promise.resolve(response({ items: missions }));
    if (input.endsWith("/vessels")) return Promise.resolve(response({ items: vessels }));
    if (input.endsWith("/environment/observations") || input.endsWith("/environment/sources")) return Promise.resolve(response({ items: [] }));
    if (input.includes("/route-candidates") || input.includes("/routes") || input.includes("/alerts")) return Promise.resolve(response({ items: [] }));
    return Promise.reject(new Error(`Unexpected request: ${input}`));
  }));
}

beforeEach(() => localStorage.setItem("kurmesh.accessToken", "test-token"));
afterEach(() => { cleanup(); localStorage.clear(); vi.unstubAllGlobals(); });

describe("MissionWorkspacePage", () => {
  it("shows the Antarctic mission empty state and create action", async () => {
    installApi(); renderWorkspace();
    expect(await screen.findByText("No missions available")).toBeInTheDocument();
    expect(screen.getByText("Create an Antarctic research mission to begin environmental analysis and route planning.")).toBeInTheDocument();
    expect(screen.getAllByRole("button", { name: "Create Mission" }).length).toBeGreaterThan(0);
  });

  it("creates a vessel with backend-provided data", async () => {
    let currentVessels: typeof vessel[] = [];
    installApi({ vessels: currentVessels, onPostVessel: () => { currentVessels = [vessel]; return response(vessel, 201); } }); renderWorkspace();
    fireEvent.click(await screen.findByRole("button", { name: "Create Mission" }));
    fireEvent.click(await screen.findByRole("button", { name: "Create vessel" }));
    fireEvent.change(screen.getByLabelText("Vessel name"), { target: { value: vessel.name } });
    fireEvent.change(screen.getByLabelText("Vessel type"), { target: { value: vessel.vessel_type } });
    fireEvent.change(screen.getByLabelText("Specifications"), { target: { value: JSON.stringify(vessel.specifications) } });
    fireEvent.click(screen.getByRole("button", { name: "Create vessel" }));
    await waitFor(() => expect(vi.mocked(fetch)).toHaveBeenCalledWith(expect.stringContaining("/vessels"), expect.objectContaining({ method: "POST" })));
    expect(await screen.findByRole("option", { name: "RV Aurora · Research vessel" })).toBeInTheDocument();
  });

  it("creates a mission and opens its mission workspace", async () => {
    let currentMissions: typeof mission[] = [];
    installApi({ vessels: [vessel], missions: currentMissions, onPostMission: () => { currentMissions = [mission]; return response(mission, 201); } }); renderWorkspace();
    fireEvent.click(await screen.findByRole("button", { name: "Create Mission" }));
    fireEvent.change(screen.getByLabelText("Mission name"), { target: { value: mission.name } });
    fireEvent.change(screen.getByLabelText("Vessel"), { target: { value: vessel.id } });
    fireEvent.change(screen.getByLabelText("Departure date and time"), { target: { value: "2026-01-10T09:00" } });
    fireEvent.click(screen.getByRole("button", { name: "Create mission" }));
    await waitFor(() => expect(vi.mocked(fetch)).toHaveBeenCalledWith(expect.stringContaining("/missions"), expect.objectContaining({ method: "POST" })));
    expect(await screen.findByText("ACTIVE MISSION")).toBeInTheDocument();
    expect(screen.getAllByText("Weddell research mission").length).toBeGreaterThan(0);
    expect(screen.getByText("Mission ID")).toBeInTheDocument();
    expect(screen.getByLabelText("Mission workflow progress")).toHaveTextContent("Environmental data");
  });

  it("shows existing backend mission details without invented route or approval controls", async () => {
    installApi({ missions: [mission], vessels: [vessel] }); renderWorkspace();
    expect(await screen.findByText("RV Aurora · Research vessel")).toBeInTheDocument();
    expect(screen.getAllByText("Not yet generated").length).toBeGreaterThan(0);
    expect(screen.queryByRole("button", { name: /approve|reject|review/i })).not.toBeInTheDocument();
  });

  it("shows a mission API error without rendering fabricated missions", async () => {
    vi.stubGlobal("fetch", vi.fn((input: string) => input.endsWith("/missions") ? Promise.resolve(response({ error: { code: "INTERNAL_ERROR", message: "failed" } }, 500)) : Promise.resolve(response({ items: [] })))); renderWorkspace();
    expect(await screen.findByText("Mission data unavailable")).toBeInTheDocument();
    expect(screen.queryByText("Antarctic Research Mission 01")).not.toBeInTheDocument();
  });
});
