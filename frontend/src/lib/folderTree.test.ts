import { describe, expect, it } from "vitest";
import { classifyTree } from "@/lib/folderTree";

const NESTED = [
  ".",
  "├── src",
  "│   ├── main.py",
  "│   └── utils",
  "│       └── paths.py",
  "└── README.md",
].join("\n");

function kindOf(source: string, name: string) {
  const line = classifyTree(source).find((entry) => entry.name === name);
  return line?.kind;
}

describe("classifyTree", () => {
  it("colors a nested name as a folder and a leaf as a file", () => {
    expect(kindOf(NESTED, "src")).toBe("folder");
    expect(kindOf(NESTED, "utils")).toBe("folder");
    expect(kindOf(NESTED, "main.py")).toBe("file");
    expect(kindOf(NESTED, "paths.py")).toBe("file");
    expect(kindOf(NESTED, "README.md")).toBe("file");
    expect(kindOf(NESTED, ".")).toBe("folder");
  });

  it("treats a trailing slash as a folder even when nothing is nested", () => {
    const source = [".", "├── empty/", "└── notes"].join("\n");
    expect(kindOf(source, "empty/")).toBe("folder");
    expect(kindOf(source, "notes")).toBe("file");
  });

  it("treats an empty folder without a slash as a file", () => {
    const source = [".", "├── notes", "└── README.md"].join("\n");
    expect(kindOf(source, "notes")).toBe("file");
  });

  it("keeps tree marks separate from the name", () => {
    const line = classifyTree(NESTED).find((entry) => entry.name === "main.py");
    expect(line?.glyphs).toBe("│   ├── ");
  });
});
