import { describe, expect, it } from "vitest";
import { cn } from "./cn";

describe("cn with Tailwind 4", () => {
  it("resolves conflicting Tailwind 4 utilities", () => {
    expect(cn("size-8", "size-10")).toBe("size-10");
    expect(cn("inset-shadow-sm", "inset-shadow-md")).toBe("inset-shadow-md");
  });

  it("preserves component classes and resolves named theme color overrides", () => {
    expect(cn("cg-input bg-surface text-fg", "bg-primary text-primary-foreground"))
      .toBe("cg-input bg-primary text-primary-foreground");
  });

  it("keeps independent variants and conditional classes", () => {
    expect(cn("bg-surface hover:bg-surface-alt", false && "hidden", { "text-fg": true }))
      .toBe("bg-surface hover:bg-surface-alt text-fg");
  });
});
