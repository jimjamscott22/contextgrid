import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, waitFor } from "@testing-library/react";

// Mock mermaid before importing the component
vi.mock("mermaid", () => ({
  default: {
    initialize: vi.fn(),
    render: vi.fn(),
  },
}));

vi.mock("@/components/ThemeProvider", () => ({
  useTheme: () => ({ themeMode: "light" }),
}));

import mermaid from "mermaid";
import { Mermaid } from "@/components/Mermaid";

const mockMermaid = mermaid as unknown as {
  initialize: ReturnType<typeof vi.fn>;
  render: ReturnType<typeof vi.fn>;
};

describe("Mermaid component error rendering", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockMermaid.initialize.mockImplementation(() => {});
  });

  it("renders error as escaped text — XSS payload is not injected as markup", async () => {
    const xssPayload = '<img src=x onerror="alert(1)">';
    mockMermaid.render.mockRejectedValue(new Error(xssPayload));

    const { container } = render(<Mermaid chart="invalid" id="test-mermaid" />);

    await waitFor(() => {
      const pre = container.querySelector("pre");
      expect(pre).not.toBeNull();
      // Text content is the raw error string (correct)
      expect(pre!.textContent).toContain("img src=x");
      // If XSS worked, innerHTML would contain a literal <img ...> tag
      // React escapes it to &lt;img ..., so the img element is never created
      expect(pre!.innerHTML).not.toContain("<img");
    });

    // If the payload were injected as HTML, an img element would exist in the document
    expect(document.querySelector("img")).toBeNull();
  });

  it("renders mermaid SVG on success without error element", async () => {
    mockMermaid.render.mockResolvedValue({ svg: "<svg><text>diagram</text></svg>" });

    const { container } = render(<Mermaid chart="graph TD; A-->B" id="test-mermaid-2" />);

    await waitFor(() => {
      const div = container.querySelector(".overflow-x-auto");
      expect(div?.innerHTML).toContain("diagram");
      // No error pre element on success
      expect(container.querySelector("pre")).toBeNull();
    });
  });
});
