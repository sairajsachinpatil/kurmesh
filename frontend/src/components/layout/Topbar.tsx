import { Menu } from "lucide-react";
import { Button } from "../ui/Button";
export function Topbar({ onMenu }: { onMenu: () => void }) { return <header className="flex min-h-18 items-center gap-3 border-b border-kurmesh-border bg-white px-4 sm:px-6"><Button variant="ghost" className="min-h-11 min-w-11 p-2 lg:hidden" aria-label="Open navigation" onClick={onMenu}><Menu aria-hidden="true" /></Button><div><p className="text-sm font-semibold text-kurmesh-muted">KURMESH</p><h1 className="text-lg font-bold text-kurmesh-text">Operational workspace</h1></div></header>; }
