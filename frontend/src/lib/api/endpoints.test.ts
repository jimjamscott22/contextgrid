import { describe, expect, it } from "vitest";

import { mapProjectQuery } from "./endpoints";

describe("mapProjectQuery", () => {
  it("forwards search to the API query string", () => {
    expect(mapProjectQuery({ search: "contextgrid" }).search).toBe("contextgrid");
  });

  it("omits empty search", () => {
    expect(mapProjectQuery({ search: "" }).search).toBeUndefined();
  });

  it.each([
    ["recent", "last_worked_at"],
    ["name", "name"],
    ["created", "created_at"],
    ["status", "status"],
  ] as const)("maps sort %s to sort_by %s", (sort, sortBy) => {
    expect(mapProjectQuery({ sort }).sort_by).toBe(sortBy);
  });

  it("forwards sort direction and omits it when unset", () => {
    expect(mapProjectQuery({ sort: "name", sort_order: "asc" }).sort_order).toBe("asc");
    expect(mapProjectQuery({ sort: "name" }).sort_order).toBeUndefined();
  });
});
