import { NavLink, Link } from "react-router-dom";
import { Menu, Moon, Sun } from "lucide-react";
import { useTheme } from "@/components/ThemeProvider";
import { cn } from "@/lib/cn";

interface NavbarProps {
  onToggleSidebar: () => void;
}

const links = [
  { to: "/projects", label: "Projects" },
  { to: "/tasks", label: "Tasks" },
  { to: "/kanban", label: "Kanban" },
  { to: "/analytics", label: "Analytics" },
];

export function Navbar({ onToggleSidebar }: NavbarProps) {
  const { theme, toggleTheme } = useTheme();

  return (
    <nav className="sticky top-0 z-40 border-b border-border bg-surface/95 backdrop-blur supports-[backdrop-filter]:bg-surface/80">
      <div className="mx-auto flex h-14 max-w-7xl items-center justify-between px-4">
        <div className="flex items-center gap-3">
          <button
            type="button"
            onClick={onToggleSidebar}
            aria-label="Toggle sidebar"
            className="rounded-md p-2 text-fg-soft hover:bg-surface-alt hover:text-fg"
          >
            <Menu size={20} />
          </button>
          <Link
            to="/"
            className="flex items-center gap-2 text-lg font-bold text-fg no-underline hover:no-underline"
          >
            <span className="inline-block h-3 w-3 rounded-sm bg-primary shadow-[inset_0_0_0_2px_rgba(255,255,255,0.35)]" />
            ContextGrid
          </Link>
        </div>

        <div className="flex items-center gap-4">
          <ul className="hidden items-center gap-1 sm:flex">
            {links.map((l) => (
              <li key={l.to}>
                <NavLink
                  to={l.to}
                  className={({ isActive }) =>
                    cn(
                      "rounded-md px-3 py-1.5 text-sm font-medium no-underline hover:no-underline transition-colors",
                      isActive
                        ? "bg-primary/10 text-primary"
                        : "text-fg-soft hover:bg-surface-alt hover:text-fg"
                    )
                  }
                >
                  {l.label}
                </NavLink>
              </li>
            ))}
          </ul>

          <button
            type="button"
            onClick={toggleTheme}
            aria-label={`Switch to ${theme === "dark" ? "light" : "dark"} mode`}
            className="rounded-md p-2 text-fg-soft hover:bg-surface-alt hover:text-fg"
          >
            {theme === "dark" ? <Sun size={18} /> : <Moon size={18} />}
          </button>
        </div>
      </div>
    </nav>
  );
}
