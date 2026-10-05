import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { FolderStructurePanel } from "@/components/project/FolderStructurePanel";

const SAVED = [".", "├── src", "│   └── main.py", "├── empty/", "└── notes"].join("\n");

function kind(name: string): string | null {
  const node = screen.getByText(name);
  return node.getAttribute("data-kind");
}

describe("FolderStructurePanel", () => {
  it("colors nested folders, slash folders, and empty folders without a slash", () => {
    render(
      <FolderStructurePanel saved={SAVED} imageUrl={null} onSave={vi.fn()} />
    );

    expect(kind("src")).toBe("folder");
    expect(kind("main.py")).toBe("file");
    expect(kind("empty/")).toBe("folder");
    expect(kind("notes")).toBe("file");
  });

  it("clears the listing when the box is emptied and saved", () => {
    const onSave = vi.fn();
    const { rerender } = render(
      <FolderStructurePanel
        saved={SAVED}
        imageUrl="https://example.com/tree.png"
        onSave={onSave}
      />
    );

    fireEvent.change(screen.getByLabelText("Folder tree"), {
      target: { value: "   " },
    });
    fireEvent.click(screen.getByRole("button", { name: "Save" }));

    expect(onSave).toHaveBeenCalledWith("");
    expect(screen.getByLabelText("Folder structure preview")).toBeTruthy();

    rerender(
      <FolderStructurePanel
        saved=""
        imageUrl="https://example.com/tree.png"
        onSave={onSave}
      />
    );

    expect(screen.queryByLabelText("Folder structure preview")).toBeNull();
    expect((screen.getByLabelText("Folder tree") as HTMLTextAreaElement).value).toBe("");
    expect(screen.getByRole("img", { name: "Folder structure diagram" })).toBeTruthy();
  });

  it("shows a stored diagram under the preview", () => {
    const { container } = render(
      <FolderStructurePanel
        saved={SAVED}
        imageUrl="https://example.com/tree.png"
        onSave={vi.fn()}
      />
    );

    const preview = screen.getByLabelText("Folder structure preview");
    const image = screen.getByRole("img", { name: "Folder structure diagram" });
    expect(image.getAttribute("src")).toBe("https://example.com/tree.png");
    expect(
      preview.compareDocumentPosition(image) & Node.DOCUMENT_POSITION_FOLLOWING
    ).toBeTruthy();
    expect(container.querySelector("input")).toBeNull();
  });

  it("does not recolor the preview while the box is edited", () => {
    render(
      <FolderStructurePanel saved={SAVED} imageUrl={null} onSave={vi.fn()} />
    );

    fireEvent.change(screen.getByLabelText("Folder tree"), {
      target: { value: "└── only-a-file.txt" },
    });

    expect(kind("src")).toBe("folder");
    expect(screen.queryByText("only-a-file.txt")).toBeNull();
  });

  it("keeps the text box when nothing is saved, including beside a diagram", () => {
    render(
      <FolderStructurePanel
        saved={null}
        imageUrl="https://example.com/tree.png"
        onSave={vi.fn()}
      />
    );

    expect((screen.getByLabelText("Folder tree") as HTMLTextAreaElement).value).toBe("");
    expect(screen.queryByLabelText("Folder structure preview")).toBeNull();
    expect(screen.getByRole("img", { name: "Folder structure diagram" })).toBeTruthy();
    expect(screen.queryByText(/edit the project/i)).toBeNull();
  });
});
