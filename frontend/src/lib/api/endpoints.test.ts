import { describe, expect, it } from "vitest";

import { mapProjectQuery } from "./endpoints";

describe("mapProjectQuery", () => {
  it("forwards search to the API query string", () => {
    expect(mapProjectQuery({ search: "contextgrid" }).search).toBe("contextgrid");
  });

  it("omits empty search", () => {
    expect(mapProjectQuery({ search: "" }).search).toBeUndefined();
  });
});
