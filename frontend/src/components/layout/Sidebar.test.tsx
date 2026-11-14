import { fireEvent, render, screen, within, cleanup } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MemoryRouter } from "react-router-dom";
import { Sidebar } from "./Sidebar";
import { api } from "@/lib/api/endpoints";
import type { Project } from "@/lib/api/types";

vi.mock("@/lib/api/endpoints", () => ({ api: { listProjects: vi.fn() } }));

const projects = [
  { id: 1, name: "Zebra", project_group: "Work", primary_language: "JS", status: "active" },
  { id: 2, name: "Alpha", project_group: "Work", primary_language: "javascript", status: "idea" },
  { id: 3, name: "Notebook", project_group: null, primary_language: null, status: "paused" },
] as Project[];

function mount() {
  return render(
    <QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}>
      <MemoryRouter><Sidebar open onClose={vi.fn()} /></MemoryRouter>
    </QueryClientProvider>
  );
}

beforeEach(() => {
  const storage = new Map<string, string>();
  vi.stubGlobal("localStorage", {
    getItem: (key: string) => storage.get(key) ?? null,
    setItem: (key: string, value: string) => storage.set(key, value),
  });
  vi.mocked(api.listProjects).mockReset();
  vi.mocked(api.listProjects).mockResolvedValue({ projects, total: projects.length });
});
afterEach(() => { cleanup(); vi.unstubAllGlobals(); });

describe("sidebar grouping", () => {
  it.each([null, "2026-11-01T12:00:00"])(
    "keeps newer projects first when Recent activity is tied at %s",
    async (last_worked_at) => {
      const tiedProjects = [
        { ...projects[0], created_at: "2026-01-01T12:00:00", last_worked_at },
        { ...projects[1], created_at: "2026-10-01T12:00:00", last_worked_at },
        {
          ...projects[2],
          created_at: "2025-01-01T12:00:00",
          last_worked_at: "2026-11-02T12:00:00",
        },
      ];
      vi.mocked(api.listProjects).mockResolvedValue({ projects: tiedProjects, total: 3 });
      mount();
      await screen.findByText("Zebra");

      const links = screen.getAllByRole("link")
        .map((link) => link.getAttribute("href"))
        .filter((href) => href?.startsWith("/projects/"));
      expect(links).toEqual(["/projects/3", "/projects/2", "/projects/1"]);
    },
  );

  it("groups, sorts, collapses, and reveals search matches", async () => {
    mount();
    await screen.findByText("Zebra");
    fireEvent.change(screen.getByLabelText("Group by"), { target: { value: "custom" } });
    fireEvent.change(screen.getByLabelText("Sort"), { target: { value: "name_asc" } });
    const work = screen.getByRole("button", { name: "Work (2 projects)" });
    const panel = document.getElementById(work.getAttribute("aria-controls")!) as HTMLDivElement;
    expect(within(panel).getAllByRole("link").map((link) => link.textContent)).toEqual(["Alphaidea", "Zebraactive"]);
    expect(screen.getByRole("button", { name: "Ungrouped (1 projects)" })).toBeTruthy();
    fireEvent.click(work);
    expect(panel.hidden).toBe(true);
    fireEvent.change(screen.getByRole("searchbox"), { target: { value: "Zebra" } });
    expect(screen.getByRole("button", { name: "Work (1 projects)" }).getAttribute("aria-expanded")).toBe("true");
    expect(screen.getByRole("link", { name: /Zebra/ })).toBeTruthy();
    expect(screen.queryByRole("button", { name: /Ungrouped/ })).toBeNull();
    expect(localStorage.getItem("cg-sidebar-group-by")).toBe("custom");
  });

  it("restores language grouping, normalizes aliases, and falls back for failed badges", async () => {
    localStorage.setItem("cg-sidebar-group-by", "language");
    mount();
    expect(await screen.findByRole("button", { name: "JavaScript (2 projects)" })).toBeTruthy();
    expect(screen.getByRole("button", { name: "Unspecified (1 projects)" })).toBeTruthy();
    const badge = screen.getAllByRole("img", { name: "JavaScript" })[0];
    expect(badge.getAttribute("src")).toContain("https://img.shields.io/");
    fireEvent.error(badge);
    expect(screen.getAllByRole("img", { name: "JavaScript" })).toHaveLength(1);
    fireEvent.change(screen.getByLabelText("Group by"), { target: { value: "none" } });
    expect(screen.getAllByRole("link").filter((link) => link.getAttribute("href")?.startsWith("/projects/"))).toHaveLength(3);
  });

  it("loads projects beyond the first page", async () => {
    vi.mocked(api.listProjects)
      .mockResolvedValueOnce({ projects: [projects[0]], total: 2 })
      .mockResolvedValueOnce({ projects: [projects[2]], total: 2 });
    mount();
    await screen.findByText("Notebook");
    expect(api.listProjects).toHaveBeenLastCalledWith(expect.objectContaining({ offset: 1, include_archived: true }));
  });
});
