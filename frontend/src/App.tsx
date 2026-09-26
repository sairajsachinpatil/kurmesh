import { useLocation } from "react-router-dom";
import { AppRoutes } from "./app/routes";
import { AppShell } from "./components/layout/AppShell";

export function App() {
  const location = useLocation();
  return location.pathname === "/login" ? <AppRoutes /> : <AppShell><AppRoutes /></AppShell>;
}
