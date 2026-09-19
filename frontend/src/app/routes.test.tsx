import { cleanup, render, screen } from "@testing-library/react";
import "@testing-library/jest-dom/vitest";
import { afterEach, describe, expect, it, vi } from "vitest";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MemoryRouter } from "react-router-dom";
import { AppShell } from "../components/layout/AppShell";
import { AppRoutes } from "./routes";
vi.mock("../components/map/OperationalMap", () => ({ OperationalMap: () => <div aria-label="Operational map" /> }));
afterEach(cleanup);
function renderPath(path: string) { const client = new QueryClient({ defaultOptions: { queries: { retry: false } } }); return render(<QueryClientProvider client={client}><MemoryRouter initialEntries={[path]}><AppShell><AppRoutes /></AppShell></MemoryRouter></QueryClientProvider>); }
describe("application navigation", () => {
  it("redirects the root route to the dashboard", () => { renderPath("/"); expect(screen.getByRole("heading", { name: "Operational dashboard", level: 2 })).toBeInTheDocument(); });
  it("shows the active dashboard navigation item", () => { renderPath("/dashboard"); expect(screen.getByRole("link", { name: "Overview" })).toHaveClass("border-kurmesh-blue"); });
  it("renders structural page placeholders without operational data", () => { renderPath("/routes"); expect(screen.getByRole("heading", { name: "Routes", level: 2 })).toBeInTheDocument(); expect(screen.getByText("Candidate routes will appear after the routing service is connected.")).toBeInTheDocument(); });
  it("renders dashboard unavailable states", () => { renderPath("/dashboard"); expect(screen.getByText("No candidate routes")).toBeInTheDocument(); expect(screen.getByLabelText("Operational map")).toBeInTheDocument(); expect(screen.getAllByLabelText("Status: Unavailable").length).toBeGreaterThan(0); });
});
