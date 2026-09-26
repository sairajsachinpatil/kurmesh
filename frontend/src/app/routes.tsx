import { type ReactNode } from "react";
import { Navigate, Route, Routes } from "react-router-dom";
import { hasAccessToken } from "../api/client";
import { DashboardPage } from "../pages/Dashboard/DashboardPage";
import { LoginPage } from "../pages/Auth/LoginPage";
import { MissionWorkspacePage } from "../pages/Missions/MissionWorkspacePage";
import { OperationsMapPage } from "../pages/OperationsMap/OperationsMapPage";
import { PagePlaceholder } from "../pages/PagePlaceholder";
const pages = [{ path: "/forecasts", title: "Forecasts", description: "Forecast data will appear when forecast services are connected." }, { path: "/routes", title: "Routes", description: "Candidate routes will appear after the routing service is connected." }, { path: "/alerts", title: "Alerts", description: "No active alerts available." }, { path: "/simulation", title: "Simulation", description: "Simulation workspaces will appear when connected." }, { path: "/audit", title: "Audit", description: "Audit records will appear when the audit service is connected." }];
function Protected({ children }: { children: ReactNode }) { return hasAccessToken() ? <>{children}</> : <Navigate to="/login" replace />; }
export function AppRoutes() { return <Routes><Route path="/login" element={<LoginPage />} /><Route path="/" element={<Navigate to="/dashboard" replace />} /><Route path="/dashboard" element={<Protected><DashboardPage /></Protected>} /><Route path="/missions" element={<Protected><MissionWorkspacePage /></Protected>} /><Route path="/operations-map" element={<Protected><OperationsMapPage /></Protected>} />{pages.map((page) => <Route key={page.path} path={page.path} element={<Protected><PagePlaceholder title={page.title} description={page.description} /></Protected>} />)}<Route path="*" element={<Navigate to="/dashboard" replace />} /></Routes>; }
