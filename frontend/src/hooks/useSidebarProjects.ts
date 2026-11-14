import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api/endpoints";
import { qk } from "@/lib/api/keys";
import type { Project } from "@/lib/api/types";

/** Fetch every page so sidebar groups and group suggestions are complete. */
export async function fetchSidebarProjects() {
  const projects: Project[] = [];
  let total = 0;
  do {
    const page = await api.listProjects({
      include_archived: true,
      limit: 50,
      offset: projects.length,
      sort: "created",
      sort_order: "asc",
    });
    total = page.total;
    projects.push(...page.projects);
    if (page.projects.length === 0) break;
  } while (projects.length < total);
  return { projects, total };
}

/** Share the full project list between sidebar navigation and group inputs. */
export function useSidebarProjects() {
  return useQuery({
    queryKey: qk.projects({ all: true, sidebar: true }),
    queryFn: fetchSidebarProjects,
  });
}
