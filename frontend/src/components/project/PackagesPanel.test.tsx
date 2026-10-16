import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { describe, expect, it, vi, beforeEach } from "vitest";
import { ToastProvider } from "@/components/Toast";
import {
  PackagesPanel,
  buildInstallCommand,
} from "@/components/project/PackagesPanel";
import { api } from "@/lib/api/endpoints";

vi.mock("@/lib/api/endpoints", () => ({
  api: {
    listPackages: vi.fn(),
    createPackage: vi.fn(),
    updatePackage: vi.fn(),
    deletePackage: vi.fn(),
  },
}));

function renderPanel(props?: Partial<React.ComponentProps<typeof PackagesPanel>>) {
  const qc = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  const onSavePackageManager = vi.fn();
  const utils = render(
    <QueryClientProvider client={qc}>
      <ToastProvider>
        <PackagesPanel
          projectId={1}
          packageManager="uv"
          onSavePackageManager={onSavePackageManager}
          {...props}
        />
      </ToastProvider>
    </QueryClientProvider>,
  );
  return { ...utils, onSavePackageManager };
}

describe("PackagesPanel", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(api.listPackages).mockResolvedValue({
      packages: [
        {
          id: 1,
          project_id: 1,
          name: "fastapi",
          version: ">=0.115.0",
          package_type: "prod",
          description: "Web API framework",
          created_at: "2026-01-01T00:00:00",
        },
        {
          id: 2,
          project_id: 1,
          name: "pytest",
          version: "^8.0.0",
          package_type: "dev",
          description: "Unit test runner",
          created_at: "2026-01-01T00:00:00",
        },
      ],
      total: 2,
    });
  });

  it("renders package manager and listed packages with install commands", async () => {
    renderPanel({ packageManager: "uv" });

    expect(
      (screen.getByLabelText("Package manager") as HTMLInputElement).value,
    ).toBe("uv");

    await waitFor(() => {
      expect(screen.getByText("fastapi")).toBeTruthy();
      expect(screen.getByText("pytest")).toBeTruthy();
    });

    expect(screen.getByText("Web API framework")).toBeTruthy();
    expect(screen.getByText('uv add "fastapi>=0.115.0"')).toBeTruthy();
    expect(screen.getByText('uv add --dev "pytest==^8.0.0"')).toBeTruthy();
  });

  it("shell-quotes uv and poetry install specs so version constraints survive copy-paste", () => {
    expect(buildInstallCommand("uv", "fastapi", ">=0.115.0", "prod")).toBe(
      'uv add "fastapi>=0.115.0"',
    );
    expect(buildInstallCommand("uv", "pytest", ">=8.0.0", "dev")).toBe(
      'uv add --dev "pytest>=8.0.0"',
    );
    expect(buildInstallCommand("poetry", "fastapi", ">=0.115.0", "prod")).toBe(
      'poetry add "fastapi>=0.115.0"',
    );
    expect(buildInstallCommand("poetry", "pytest", ">=8.0.0", "dev")).toBe(
      'poetry add --group dev "pytest>=8.0.0"',
    );
  });

  it("allows selecting a preset and saving the package manager", async () => {
    const { onSavePackageManager } = renderPanel({ packageManager: "npm" });

    fireEvent.click(screen.getByRole("button", { name: "pnpm" }));
    expect(
      (screen.getByLabelText("Package manager") as HTMLInputElement).value,
    ).toBe("pnpm");

    fireEvent.click(screen.getByRole("button", { name: "Save manager" }));
    await waitFor(() => {
      expect(onSavePackageManager).toHaveBeenCalledWith("pnpm");
    });
  });

  it("adds a new package with details", async () => {
    vi.mocked(api.createPackage).mockResolvedValue({
      id: 3,
      project_id: 1,
      name: "httpx",
      version: ">=0.27.0",
      package_type: "prod",
      description: "Async HTTP client",
      created_at: "2026-01-01T00:00:00",
    });

    renderPanel();

    await waitFor(() => {
      expect(screen.getByText("fastapi")).toBeTruthy();
    });

    fireEvent.change(
      screen.getByPlaceholderText("Package name (e.g. fastapi, react)"),
      { target: { value: "httpx" } },
    );
    fireEvent.change(
      screen.getByPlaceholderText("Version (e.g. ^18.3.0)"),
      { target: { value: ">=0.27.0" } },
    );
    fireEvent.change(
      screen.getByPlaceholderText(
        "Details / purpose (optional, e.g. HTTP client for async API calls)",
      ),
      { target: { value: "Async HTTP client" } },
    );

    fireEvent.click(screen.getByRole("button", { name: "Add package" }));

    await waitFor(() => {
      expect(api.createPackage).toHaveBeenCalledWith(1, {
        name: "httpx",
        version: ">=0.27.0",
        package_type: "prod",
        description: "Async HTTP client",
      });
    });
  });

  it("filters packages by dependency type", async () => {
    renderPanel();

    await waitFor(() => {
      expect(screen.getByText("fastapi")).toBeTruthy();
      expect(screen.getByText("pytest")).toBeTruthy();
    });

    fireEvent.change(screen.getByLabelText("Filter packages by type"), {
      target: { value: "dev" },
    });

    expect(screen.queryByText("fastapi")).toBeNull();
    expect(screen.getByText("pytest")).toBeTruthy();
  });
});
