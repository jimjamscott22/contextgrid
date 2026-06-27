import { NavLink, Link } from "react-router-dom";
import { Code2, GitBranch, Menu, Palette, Terminal } from "lucide-react";
import { useTheme } from "@/components/ThemeProvider";
import { Select } from "@/components/ui/Input";
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

const softwareIcons = [
  { Icon: Code2, className: "border-primary/20 bg-primary/10 text-primary" },
  { Icon: GitBranch, className: "border-accent/20 bg-accent/10 text-accent" },
  { Icon: Terminal, className: "border-success/20 bg-success/10 text-success" },
];

export function Navbar({ onToggleSidebar }: NavbarProps) {
  const { theme, themes, setTheme } = useTheme();

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
          <div
            aria-hidden="true"
            className="hidden items-center gap-1.5 min-[430px]:flex"
          >
            {softwareIcons.map(({ Icon, className }, index) => (
              <span
                key={index}
                className={cn(
                  "inline-flex h-7 w-7 shrink-0 items-center justify-center rounded-md border",
                  className
                )}
              >
                <Icon size={15} strokeWidth={2} />
              </span>
            ))}
          </div>
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

          <label className="flex items-center gap-2 text-fg-soft">
            <Palette size={18} aria-hidden="true" />
            <span className="sr-only">Theme</span>
            <Select
              aria-label="Theme"
              value={theme}
              onChange={(event) => setTheme(event.target.value as typeof theme)}
              className="h-9 w-[9.5rem] py-1.5 text-xs"
            >
              <optgroup label="Editor Themes">
                {themes.filter((o) => o.group === "editor").map((option) => (
                  <option key={option.id} value={option.id}>
                    {option.label}
                  </option>
                ))}
              </optgroup>
              <optgroup label="Lifestyle Themes">
                {themes.filter((o) => o.group === "lifestyle").map((option) => (
                  <option key={option.id} value={option.id}>
                    {option.label}
                  </option>
                ))}
              </optgroup>
            </Select>
          </label>
        </div>
      </div>
    </nav>
  );
}
