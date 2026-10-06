/** Maximum stored listing length, matching the API field cap. */
export const FOLDER_STRUCTURE_MAX_LENGTH = 65535;

export type TreeKind = "folder" | "file" | "plain";

export interface TreeLine {
  glyphs: string;
  name: string;
  depth: number;
  kind: TreeKind;
}

const CONNECTOR =
  /^(.*?)(├── |└── |\|\-\- |`\-\- |\+\-\- |\\-\- )(.*)$/;

/**
 * Split one listing line into quiet tree marks and the name they introduce.
 * Depth is the character index where the name starts, so a later line is
 * nested when its depth is greater.
 */
function splitLine(line: string): Pick<TreeLine, "glyphs" | "name" | "depth"> {
  const normalized = line.replace(/\u00a0/g, " ");
  const connector = normalized.match(CONNECTOR);
  if (connector && /^[│| ]*$/.test(connector[1])) {
    const glyphLength = connector[1].length + connector[2].length;
    return {
      glyphs: line.slice(0, glyphLength),
      name: line.slice(glyphLength),
      depth: glyphLength,
    };
  }
  const indent = normalized.match(/^\s*/)?.[0].length ?? 0;
  return {
    glyphs: line.slice(0, indent),
    name: line.slice(indent),
    depth: indent,
  };
}

/**
 * Classify each line of a pasted tree listing.
 * A named line is a folder when its name ends in `/` or a later named line
 * sits deeper. Every other named line is a file. Blank lines stay plain.
 */
export function classifyTree(source: string): TreeLine[] {
  const lines = source.split(/\r?\n/).map((line) => {
    const split = splitLine(line);
    return { ...split, kind: "file" as TreeKind };
  });

  for (let i = 0; i < lines.length; i += 1) {
    const name = lines[i].name.trim();
    if (!name) {
      lines[i].kind = "plain";
      continue;
    }
    if (name.endsWith("/")) {
      lines[i].kind = "folder";
      continue;
    }
    let nested = false;
    for (let j = i + 1; j < lines.length; j += 1) {
      if (!lines[j].name.trim()) continue;
      nested = lines[j].depth > lines[i].depth;
      break;
    }
    lines[i].kind = nested ? "folder" : "file";
  }

  return lines;
}
