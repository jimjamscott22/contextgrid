import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { ProjectForm } from "@/components/forms/ProjectForm";

const EXPECTED_OPTIONS = [
  ["", "—"],
  ["web-app", "Web App"],
  ["cli", "CLI"],
  ["documentation", "Documentation"],
  ["college", "College"],
  ["desktop-app", "Desktop"],
  ["pwa", "PWA"],
  ["llm-integrated", "LLM-based/integrated"],
  ["website", "Website"],
];

describe("ProjectForm project type selector", () => {
  it("renders the canonical project types in the approved order", () => {
    render(<ProjectForm onSubmit={vi.fn()} />);

    const select = screen.getByLabelText("Type") as HTMLSelectElement;
    const options = Array.from(select.options).map((option) => [
      option.value,
      option.textContent,
    ]);

    expect(options).toEqual(EXPECTED_OPTIONS);
    expect(options.map(([value]) => value)).not.toContain("other");
  });

  it("submits the canonical value selected by the user", async () => {
    const onSubmit = vi.fn();
    render(<ProjectForm onSubmit={onSubmit} />);

    fireEvent.change(screen.getByLabelText("Name"), {
      target: { value: "Portfolio" },
    });
    fireEvent.change(screen.getByLabelText("Type"), {
      target: { value: "desktop-app" },
    });
    fireEvent.submit(screen.getByRole("button", { name: "Save" }).closest("form")!);

    await waitFor(() => {
      expect(onSubmit).toHaveBeenCalledWith(
        expect.objectContaining({
          name: "Portfolio",
          project_type: "desktop-app",
        })
      );
    });
  });
});
