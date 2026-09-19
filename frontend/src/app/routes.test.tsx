import { cleanup, render, screen } from "@testing-library/react";
import "@testing-library/jest-dom/vitest";
import { afterEach, describe, expect, it } from "vitest";
import { MemoryRouter } from "react-router-dom";
import { AppShell } from "../components/layout/AppShell";
import { AppRoutes } from "./routes";
afterEach(cleanup);
function renderPath(path: string) { return render(<MemoryRouter initialEntries={[path]}><AppShell><AppRoutes /></AppShell></MemoryRouter>); }
describe("application navigation", () => {
  it("redirects the root route to the dashboard", () => { renderPath("/"); expect(screen.getByRole("heading", { name: "Operational dashboard", level: 2 })).toBeInTheDocument(); });
  it("shows the active dashboard navigation item", () => { renderPath("/dashboard"); expect(screen.getByRole("link", { name: "Overview" })).toHaveClass("border-kurmesh-blue"); });
  it("renders structural page placeholders without operational data", () => { renderPath("/routes"); expect(screen.getByRole("heading", { name: "Routes", level: 2 })).toBeInTheDocument(); expect(screen.getByText("Candidate routes will appear after the routing service is connected.")).toBeInTheDocument(); });
  it("renders dashboard empty states", () => { renderPath("/dashboard"); expect(screen.getByText("No candidate routes")).toBeInTheDocument(); expect(screen.getByText("Operational map awaiting connection")).toBeInTheDocument(); });
});
