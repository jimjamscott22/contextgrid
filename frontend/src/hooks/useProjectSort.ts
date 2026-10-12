import { useCallback, useState } from "react";

const STORAGE_KEY = "cg-project-sort";

export const PROJECT_SORT_FIELDS = ["custom", "recent", "name", "status", "created"] as const;
export type ProjectSortField = (typeof PROJECT_SORT_FIELDS)[number];
export type SortDirection = "asc" | "desc";

export const PROJECT_SORT_LABELS: Record<ProjectSortField, string> = {
  custom: "Custom (drag)",
  recent: "Last worked",
  name: "Name",
  status: "Status",
  created: "Date created",
};

const DEFAULT_DIRECTION: Record<ProjectSortField, SortDirection> = {
  custom: "desc",
  recent: "desc",
  created: "desc",
  name: "asc",
  status: "asc",
};

interface SortState {
  field: ProjectSortField;
  direction: SortDirection;
}

const DEFAULT_STATE: SortState = { field: "custom", direction: DEFAULT_DIRECTION.custom };

function readSort(): SortState {
  try {
    const value: unknown = JSON.parse(localStorage.getItem(STORAGE_KEY) ?? "null");
    if (typeof value === "object" && value !== null) {
      const { field, direction } = value as Record<string, unknown>;
      if (
        PROJECT_SORT_FIELDS.includes(field as ProjectSortField) &&
        (direction === "asc" || direction === "desc")
      ) {
        return { field: field as ProjectSortField, direction };
      }
    }
  } catch {
    // Invalid or unavailable storage falls back to the custom order.
  }
  return DEFAULT_STATE;
}

function writeSort(state: SortState): void {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
  } catch {
    // The choice still applies for this session when storage is unavailable.
  }
}

/** Track the Projects page sort field and direction, remembered per browser. */
export function useProjectSort() {
  const [state, setState] = useState<SortState>(readSort);

  const setField = useCallback((field: ProjectSortField) => {
    const next = { field, direction: DEFAULT_DIRECTION[field] };
    setState(next);
    writeSort(next);
  }, []);

  const toggleDirection = useCallback(() => {
    setState((previous) => {
      const next: SortState = {
        ...previous,
        direction: previous.direction === "asc" ? "desc" : "asc",
      };
      writeSort(next);
      return next;
    });
  }, []);

  // The custom order starts from recent activity; other fields sort server-side.
  const query =
    state.field === "custom"
      ? ({ sort: "recent", sort_order: "desc" } as const)
      : ({ sort: state.field, sort_order: state.direction } as const);

  return {
    field: state.field,
    direction: state.direction,
    isCustom: state.field === "custom",
    setField,
    toggleDirection,
    query,
  };
}
