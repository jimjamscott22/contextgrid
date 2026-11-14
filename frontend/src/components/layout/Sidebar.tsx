import { useMemo, useState } from "react";
import { Link, NavLink } from "react-router-dom";
import { ChevronDown, ChevronRight, X } from "lucide-react";
import { useSidebarProjects } from "@/hooks/useSidebarProjects";
import { LanguageBadge } from "@/components/project/LanguageBadge";
import { projectLanguage } from "@/lib/projectLanguages";
import type { Project } from "@/lib/api/types";
import { Input, Select } from "@/components/ui/Input";
import { StatusBadge } from "@/components/ui/Badge";
import { cn } from "@/lib/cn";

interface SidebarProps {
  open: boolean;
  onClose: () => void;
}

const secondaryLinks = [
  { to: "/", label: "Overview", end: true },
  { to: "/graph", label: "Graph" },
  { to: "/tags", label: "Tags" },
  { to: "/templates", label: "Templates" },
  { to: "/diagrams", label: "Diagrams" },
];

type SortKey =
  | "recent"
  | "oldest_recent"
  | "newest"
  | "oldest"
  | "name_asc"
  | "name_desc";

type GroupBy = "none" | "custom" | "language";

interface ProjectGroup {
  key: string;
  name: string;
  projects: Project[];
}

export function Sidebar({ open, onClose }: SidebarProps) {
  const [search, setSearch] = useState("");
  const [groupBy, setGroupBy] = useState<GroupBy>(() => {
    try {
      const value = localStorage.getItem("cg-sidebar-group-by");
      if (value === "custom" || value === "language") return value;
    } catch { /* Storage may be unavailable. */ }
    return "none";
  });
  const [collapsed, setCollapsed] = useState<Set<string>>(new Set());
  const [sort, setSort] = useState<SortKey>(() => {
    try {
      const stored = localStorage.getItem("cg-sidebar-sort");
      if (stored && ["recent","oldest_recent","newest","oldest","name_asc","name_desc"].includes(stored))
        return stored as SortKey;
    } catch {
      // ignore
    }
    return "recent";
  });

  const { data, isPending, isError } = useSidebarProjects();

  const projects = useMemo(() => {
    const list = data?.projects ?? [];
    const filtered = search
      ? list.filter((p) => p.name.toLowerCase().includes(search.toLowerCase()))
      : list;
    const sorted = [...filtered];
    sorted.sort((a, b) => {
      switch (sort) {
        case "name_asc":
          return a.name.localeCompare(b.name);
        case "name_desc":
          return b.name.localeCompare(a.name);
        case "newest":
          return (b.created_at || "").localeCompare(a.created_at || "");
        case "oldest":
          return (a.created_at || "").localeCompare(b.created_at || "");
        case "oldest_recent":
          return (a.last_worked_at || "").localeCompare(b.last_worked_at || "");
        case "recent":
        default:
          return (b.last_worked_at || "").localeCompare(a.last_worked_at || "")
            || (b.created_at || "").localeCompare(a.created_at || "");
      }
    });
    return sorted;
  }, [data, search, sort]);

  const groups = useMemo(() => {
    if (groupBy === "none") return [{ key: "all", name: "", projects }];
    const grouped = new Map<string, ProjectGroup>();
    for (const project of projects) {
      const name = groupBy === "custom"
        ? project.project_group?.trim()
        : projectLanguage(project.primary_language)?.name;
      // Use a separate key for missing values, even if a real group has that name.
      const key = name ? `named:${name.toLowerCase()}` : "missing";
      let group = grouped.get(key);
      if (!group) {
        group = { key, name: name || (groupBy === "custom" ? "Ungrouped" : "Unspecified"), projects: [] };
        grouped.set(key, group);
      }
      group.projects.push(project);
    }
    return Array.from(grouped.values()).sort((a, b) =>
      a.key === "missing" ? 1 : b.key === "missing" ? -1 : a.name.localeCompare(b.name)
    );
  }, [projects, groupBy]);

  const handleGroupBy = (value: GroupBy) => {
    setGroupBy(value);
    try {
      localStorage.setItem("cg-sidebar-group-by", value);
    } catch { /* The selection still works without storage. */ }
  };

  const toggleGroup = (key: string) => {
    setCollapsed((previous) => {
      const next = new Set(previous);
      if (next.has(key)) next.delete(key);
      else next.add(key);
      return next;
    });
  };

  const handleSort = (value: SortKey) => {
    setSort(value);
    try {
      localStorage.setItem("cg-sidebar-sort", value);
    } catch {
      // ignore
    }
  };

  return (
    <>
      {/* overlay */}
      <div
        onClick={onClose}
        className={cn(
          "fixed inset-0 z-40 bg-black/50 backdrop-blur-sm lg:hidden",
          open ? "block" : "hidden"
        )}
      />

      <aside
        aria-label="Workspace navigation"
        aria-hidden={!open}
        className={cn(
          "fixed left-0 top-14 z-40 flex h-[calc(100vh-3.5rem)] w-[280px] flex-col border-r border-border bg-surface transition-transform",
          open ? "translate-x-0" : "-translate-x-full"
        )}
      >
        <div className="flex items-center justify-between border-b border-border p-3">
          <h3 className="text-sm font-semibold uppercase tracking-wider text-fg-soft">
            Workspace
          </h3>
          <button
            type="button"
            onClick={onClose}
            aria-label="Close sidebar"
            className="rounded-md p-1 text-fg-soft hover:bg-surface-alt hover:text-fg"
          >
            <X size={16} />
          </button>
        </div>

        <nav className="border-b border-border p-2">
          {secondaryLinks.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              end={link.end}
              onClick={() => {
                if (window.innerWidth < 1024) onClose();
              }}
              className={({ isActive }) =>
                cn(
                  "block rounded-md px-3 py-2 text-sm no-underline hover:no-underline",
                  isActive
                    ? "bg-primary/10 text-primary"
                    : "text-fg-soft hover:bg-surface-alt hover:text-fg"
                )
              }
            >
              {link.label}
            </NavLink>
          ))}
        </nav>

        <div className="space-y-2 border-b border-border p-3">
          <Input
            type="search"
            aria-label="Search projects"
            placeholder="Search projects..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
          <div className="flex items-center gap-2">
            <label htmlFor="cg-sidebar-sort" className="text-xs text-fg-soft">
              Sort
            </label>
            <Select
              id="cg-sidebar-sort"
              value={sort}
              onChange={(e) => handleSort(e.target.value as SortKey)}
              className="h-8 text-xs"
            >
              <option value="recent">Most Recent</option>
              <option value="oldest_recent">Least Recent</option>
              <option value="newest">Newest</option>
              <option value="oldest">Oldest</option>
              <option value="name_asc">Name (A-Z)</option>
              <option value="name_desc">Name (Z-A)</option>
            </Select>
          </div>
          <div className="flex items-center gap-2">
            <label htmlFor="cg-sidebar-group-by" className="shrink-0 text-xs text-fg-soft">Group by</label>
            <Select
              id="cg-sidebar-group-by"
              value={groupBy}
              onChange={(e) => handleGroupBy(e.target.value as GroupBy)}
              className="h-8 text-xs"
            >
              <option value="none">None</option>
              <option value="custom">Custom group</option>
              <option value="language">Language</option>
            </Select>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto p-2">
          {isPending && <p className="px-3 py-4 text-sm text-fg-soft">Loading projects...</p>}
          {isError && <p role="alert" className="px-3 py-4 text-sm text-fg-soft">Could not load projects.</p>}
          {!isPending && !isError && projects.length === 0 && (
            <p className="px-3 py-4 text-sm text-fg-soft">No projects found</p>
          )}
          {groups.map((group, index) => {
            const key = `${groupBy}:${group.key}`;
            // Search reveals matching projects even in collapsed sections.
            const expanded = Boolean(search) || !collapsed.has(key);
            const panelId = `cg-sidebar-group-${index}`;
            return (
              <section key={key}>
                {groupBy !== "none" && (
                  <button
                    type="button"
                    aria-label={`${group.name} (${group.projects.length} projects)`}
                    aria-expanded={expanded}
                    aria-controls={panelId}
                    onClick={() => toggleGroup(key)}
                    disabled={Boolean(search)}
                    className="flex w-full items-center gap-1 rounded-md px-2 py-2 text-xs font-semibold text-fg-soft hover:bg-surface-alt"
                  >
                    {expanded ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
                    <span className="min-w-0 flex-1 truncate text-left" title={group.name}>{group.name}</span>
                    <span>{group.projects.length}</span>
                  </button>
                )}
                <div id={panelId} hidden={groupBy !== "none" && !expanded}>
                  {group.projects.map((p) => (
                    <Link
                      key={p.id}
                      to={`/projects/${p.id}`}
                      onClick={() => {
                        if (window.innerWidth < 1024) onClose();
                      }}
                      className="group flex items-center justify-between gap-2 rounded-md px-3 py-2 text-sm text-fg no-underline hover:bg-surface-alt hover:no-underline"
                    >
                      <span className="min-w-0 flex-1 space-y-1">
                        <span className="block truncate" title={p.name}>{p.name}</span>
                        <StatusBadge status={p.status} />
                      </span>
                      <LanguageBadge language={p.primary_language} />
                    </Link>
                  ))}
                </div>
              </section>
            );
          })}
        </div>
      </aside>
    </>
  );
}
