import { describe, it, expect } from "vitest";
import { lastNDays, toISODate, shiftDays, mostActiveProject } from "@/lib/activity";
import type { ActivityDay } from "@/lib/api/types";

const today = new Date(Date.UTC(2026, 5, 21)); // 2026-06-21

describe("toISODate / shiftDays", () => {
  it("formats UTC dates", () => {
    expect(toISODate(today)).toBe("2026-06-21");
  });
  it("shifts by whole days", () => {
    expect(toISODate(shiftDays(today, -2))).toBe("2026-06-19");
  });
});

describe("lastNDays", () => {
  it("returns exactly n ascending days ending today, zero-filled", () => {
    const input: ActivityDay[] = [
      { date: "2026-06-20", count: 3, projects: "A" },
      { date: "2026-06-18", count: 1, projects: "B" },
      { date: "2026-01-01", count: 9, projects: "C" }, // outside window
    ];
    const out = lastNDays(input, 7, today);
    expect(out).toHaveLength(7);
    expect(out[0].date).toBe("2026-06-15");
    expect(out[6].date).toBe("2026-06-21");
    expect(out[6].count).toBe(0); // today, no data
    expect(out[5].count).toBe(3); // 2026-06-20
    expect(out[3].count).toBe(1); // 2026-06-18
    expect(out[4].count).toBe(0); // 2026-06-19 gap
  });
});

describe("mostActiveProject", () => {
  it("returns the most frequently appearing project", () => {
    const input: ActivityDay[] = [
      { date: "2026-06-20", count: 2, projects: "Alpha, Beta" },
      { date: "2026-06-19", count: 1, projects: "Alpha" },
      { date: "2026-06-18", count: 1, projects: "Beta" },
    ];
    expect(mostActiveProject(input)).toBe("Alpha"); // 2 appearances vs 2... tie -> alpha
  });
  it("breaks ties alphabetically", () => {
    const input: ActivityDay[] = [
      { date: "2026-06-20", count: 1, projects: "Zeta" },
      { date: "2026-06-19", count: 1, projects: "Alpha" },
    ];
    expect(mostActiveProject(input)).toBe("Alpha");
  });
  it("returns null when there is no activity", () => {
    expect(mostActiveProject([{ date: "2026-06-20", count: 0, projects: "" }])).toBeNull();
    expect(mostActiveProject([])).toBeNull();
  });
});
