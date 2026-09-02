import { useEffect, useMemo, useState } from "react";
import { arrayMove } from "@dnd-kit/sortable";
import type { Project } from "@/lib/api/types";

const STORAGE_KEY = "cg-project-order";

function readOrder(): number[] | null {
  try {
    const value: unknown = JSON.parse(localStorage.getItem(STORAGE_KEY) ?? "null");
    if (
      Array.isArray(value) &&
      value.length > 0 &&
      value.every((id) => Number.isSafeInteger(id) && id > 0)
    ) {
      return [...new Set<number>(value)];
    }
  } catch {
    // Invalid or unavailable storage falls back to recent activity.
  }
  return null;
}

/** Keep a browser-local card order while preserving projects hidden by filters. */
export function useProjectOrder(projects: Project[]) {
  const [order, setOrder] = useState<number[] | null>(readOrder);
  const [storageError, setStorageError] = useState(false);

  const orderedProjects = useMemo(() => {
    if (order === null) return projects;
    const positions = new Map(order.map((id, index) => [id, index]));
    return [...projects].sort(
      (a, b) =>
        (positions.get(a.id) ?? order.length) - (positions.get(b.id) ?? order.length),
    );
  }, [projects, order]);

  useEffect(() => {
    if (order === null) return;
    const known = new Set(order);
    const added = projects.map((p) => p.id).filter((id) => !known.has(id));
    if (added.length > 0) setOrder([...order, ...added]);
  }, [projects, order]);

  useEffect(() => {
    try {
      if (order === null) localStorage.removeItem(STORAGE_KEY);
      else localStorage.setItem(STORAGE_KEY, JSON.stringify(order));
      setStorageError(false);
    } catch {
      setStorageError(true);
    }
  }, [order]);

  const moveProject = (activeId: number, overId: number) => {
    const visibleIds = orderedProjects.map((p) => p.id);
    const from = visibleIds.indexOf(activeId);
    const to = visibleIds.indexOf(overId);
    if (from < 0 || to < 0 || from === to) return;

    const moved = arrayMove(visibleIds, from, to);
    const visible = new Set(visibleIds);
    setOrder((previous) => {
      const known = new Set(previous ?? []);
      const complete = [
        ...(previous ?? []),
        ...visibleIds.filter((id) => !known.has(id)),
      ];
      let index = 0;
      // Only replace visible slots; filtered-out projects keep their positions.
      return complete.map((id) => (visible.has(id) ? moved[index++] : id));
    });
  };

  return {
    orderedProjects,
    hasCustomOrder: order !== null,
    storageError,
    moveProject,
    resetOrder: () => setOrder(null),
  };
}
