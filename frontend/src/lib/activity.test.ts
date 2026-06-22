import { describe, it, expect } from "vitest";
import { lastNDays, toISODate, shiftDays, mostActiveProject, buildHeatmap, resolveToday } from "@/lib/activity";
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

describe("buildHeatmap", () => {
  // today = 2026-06-21 is a Sunday (getUTCDay() === 0).
  it("pads the start to align the first day to its weekday row", () => {
    // window of 8 days: 2026-06-14 (Sun) .. 2026-06-21 (Sun)
    const out = buildHeatmap([], 8, today);
    // 2026-06-14 is a Sunday -> 0 leading pads
    expect(out.cells.filter((c) => c.date === null)).toHaveLength(0);
    expect(out.cells[0].date).toBe("2026-06-14");
  });

  it("adds leading pads when the window does not start on Sunday", () => {
    // window of 5 days: 2026-06-17 (Wed=3) .. 2026-06-21 (Sun)
    const out = buildHeatmap([], 5, today);
    const pads = out.cells.filter((c) => c.date === null);
    expect(pads).toHaveLength(3); // Sun,Mon,Tue placeholders before Wed
    expect(out.cells[3].date).toBe("2026-06-17");
  });

  it("buckets counts into levels 1-4 and 0 for empty", () => {
    const input: ActivityDay[] = [
      { date: "2026-06-21", count: 8, projects: "A" }, // max -> level 4
      { date: "2026-06-20", count: 2, projects: "A" }, // 2/8=0.25 -> level 1
      { date: "2026-06-19", count: 4, projects: "A" }, // 4/8=0.5 -> level 2
      { date: "2026-06-18", count: 6, projects: "A" }, // 6/8=0.75 -> level 3
    ];
    const out = buildHeatmap(input, 4, today); // Thu..Sun, 4 leading pads (Thu=4)
    const byDate = (d: string) => out.cells.find((c) => c.date === d)!;
    expect(byDate("2026-06-21").level).toBe(4);
    expect(byDate("2026-06-20").level).toBe(1);
    expect(byDate("2026-06-19").level).toBe(2);
    expect(byDate("2026-06-18").level).toBe(3);
  });

  it("reports the number of week columns and month labels", () => {
    const out = buildHeatmap([], 8, today);
    expect(out.weeks).toBe(2); // 8 days span 2 Sunday-started columns
    expect(out.months[0]).toEqual({ label: "Jun", column: 0 });
  });
});

describe("resolveToday", () => {
  it("returns now when no payload date is ahead of the clock", () => {
    const now = new Date(Date.UTC(2026, 5, 21, 10)); // 2026-06-21T10:00Z
    const days: ActivityDay[] = [{ date: "2026-06-21", count: 1, projects: "A" }];
    expect(toISODate(resolveToday(days, now))).toBe("2026-06-21");
  });
  it("extends to a payload date ahead of the client clock", () => {
    const now = new Date(Date.UTC(2026, 5, 21, 10));
    const days: ActivityDay[] = [{ date: "2026-06-22", count: 1, projects: "A" }];
    expect(toISODate(resolveToday(days, now))).toBe("2026-06-22");
  });
  it("handles an empty payload", () => {
    const now = new Date(Date.UTC(2026, 5, 21, 10));
    expect(toISODate(resolveToday([], now))).toBe("2026-06-21");
  });
});
