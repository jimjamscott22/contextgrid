import { useEffect, useState, type ReactNode } from "react";
import { useLocation } from "react-router-dom";
import { Navbar } from "./Navbar";
import { Sidebar } from "./Sidebar";
import { cn } from "@/lib/cn";

export function AppShell({ children }: { children: ReactNode }) {
  const [sidebarOpen, setSidebarOpen] = useState<boolean>(() => {
    if (typeof window === "undefined") return false;
    if (window.innerWidth < 1024) return false;
    try {
      return localStorage.getItem("cg-sidebar") !== "closed";
    } catch {
      return true;
    }
  });

  const location = useLocation();

  useEffect(() => {
    if (window.innerWidth < 1024) {
      setSidebarOpen(false);
    }
  }, [location.pathname]);

  const handleToggle = () => {
    setSidebarOpen((prev) => {
      const next = !prev;
      try {
        localStorage.setItem("cg-sidebar", next ? "open" : "closed");
      } catch {
        // ignore
      }
      return next;
    });
  };

  return (
    <div className="flex min-h-screen flex-col">
      <Navbar onToggleSidebar={handleToggle} />
      <Sidebar open={sidebarOpen} onClose={() => setSidebarOpen(false)} />
      <main
        className={cn(
          "flex-1 transition-[padding] duration-200",
          sidebarOpen ? "lg:pl-[280px]" : "lg:pl-0"
        )}
      >
        <div className="mx-auto max-w-7xl px-4 py-6">{children}</div>
      </main>
      <footer className="border-t border-border bg-surface py-4 text-center text-xs text-fg-soft">
        ContextGrid &mdash; Track what you&apos;re building, where it lives, and what&apos;s next.
      </footer>
    </div>
  );
}
