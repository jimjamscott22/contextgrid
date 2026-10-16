import { useEffect, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Check, Copy, Edit3, Package, Trash2, X } from "lucide-react";
import { api } from "@/lib/api/endpoints";
import { qk } from "@/lib/api/keys";
import {
  PACKAGE_MANAGERS,
  PACKAGE_TYPES,
  PACKAGE_TYPE_LABELS,
  type PackageType,
  type ProjectPackage,
} from "@/lib/api/types";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Input, Select } from "@/components/ui/Input";
import { LoadingState, EmptyState } from "@/components/ui/Empty";
import { useToast } from "@/components/Toast";

interface PackagesPanelProps {
  projectId: number;
  packageManager: string | null;
  onSavePackageManager: (value: string) => Promise<unknown> | void;
  savingPackageManager?: boolean;
}

function buildInstallCommand(
  manager: string | null,
  pkgName: string,
  version: string | null,
  pkgType: PackageType,
): string {
  const pm = (manager || "").trim().toLowerCase();
  const spec = version ? `${pkgName}@${version}` : pkgName;
  const pySpec = version
    ? /^[<>=!~]/.test(version)
      ? `${pkgName}${version}`
      : `${pkgName}==${version}`
    : pkgName;

  switch (pm) {
    case "pnpm":
      return `pnpm add ${pkgType === "dev" ? "-D " : ""}${spec}`;
    case "yarn":
      return `yarn add ${pkgType === "dev" ? "--dev " : ""}${spec}`;
    case "bun":
      return `bun add ${pkgType === "dev" ? "-d " : ""}${spec}`;
    case "uv":
      return `uv add ${pkgType === "dev" ? "--dev " : ""}${pySpec}`;
    case "pip":
      return `pip install "${pySpec}"`;
    case "poetry":
      return `poetry add ${pkgType === "dev" ? "--group dev " : ""}${pySpec}`;
    case "cargo":
      return `cargo add ${pkgType === "dev" ? "--dev " : ""}${pkgName}${version ? `@${version}` : ""}`;
    case "go":
      return `go get ${pkgName}${version ? `@${version}` : ""}`;
    case "composer":
      return `composer require ${pkgType === "dev" ? "--dev " : ""}${pkgName}${version ? `:${version}` : ""}`;
    case "npm":
    default:
      return `${pm || "npm"} install ${pkgType === "dev" ? "-D " : ""}${spec}`;
  }
}

const TYPE_BADGE_CLASSES: Record<PackageType, string> = {
  prod: "border-primary/40 bg-primary/10 text-primary",
  dev: "border-warning/40 bg-warning/10 text-warning",
  optional: "border-border bg-surface-alt text-fg-soft",
  peer: "border-success/40 bg-success/10 text-success",
  other: "border-border bg-surface-alt text-fg-soft",
};

export function PackagesPanel({
  projectId,
  packageManager,
  onSavePackageManager,
  savingPackageManager = false,
}: PackagesPanelProps) {
  const savedManager = packageManager ?? "";
  const [managerDraft, setManagerDraft] = useState(savedManager);

  const [name, setName] = useState("");
  const [version, setVersion] = useState("");
  const [packageType, setPackageType] = useState<PackageType>("prod");
  const [description, setDescription] = useState("");
  const [typeFilter, setTypeFilter] = useState<PackageType | "all">("all");

  const [editingId, setEditingId] = useState<number | null>(null);
  const [editName, setEditName] = useState("");
  const [editVersion, setEditVersion] = useState("");
  const [editType, setEditType] = useState<PackageType>("prod");
  const [editDescription, setEditDescription] = useState("");

  const qc = useQueryClient();
  const { toast } = useToast();

  useEffect(() => {
    setManagerDraft(savedManager);
  }, [savedManager]);

  const { data, isLoading } = useQuery({
    queryKey: qk.packages(projectId),
    queryFn: () => api.listPackages(projectId),
  });

  const createMut = useMutation({
    mutationFn: () =>
      api.createPackage(projectId, {
        name: name.trim(),
        version: version.trim() || null,
        package_type: packageType,
        description: description.trim() || null,
      }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: qk.packages(projectId) });
      setName("");
      setVersion("");
      setPackageType("prod");
      setDescription("");
      toast("Package added", "success");
    },
    onError: (e) => toast(`Add package failed: ${(e as Error).message}`, "error"),
  });

  const updateMut = useMutation({
    mutationFn: (id: number) =>
      api.updatePackage(id, {
        name: editName.trim(),
        version: editVersion.trim(),
        package_type: editType,
        description: editDescription.trim(),
      }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: qk.packages(projectId) });
      setEditingId(null);
      toast("Package updated", "success");
    },
    onError: (e) => toast(`Update failed: ${(e as Error).message}`, "error"),
  });

  const deleteMut = useMutation({
    mutationFn: (id: number) => api.deletePackage(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: qk.packages(projectId) });
      toast("Package removed", "success");
    },
    onError: (e) => toast(`Delete failed: ${(e as Error).message}`, "error"),
  });

  const startEdit = (pkg: ProjectPackage) => {
    setEditingId(pkg.id);
    setEditName(pkg.name);
    setEditVersion(pkg.version ?? "");
    setEditType(pkg.package_type);
    setEditDescription(pkg.description ?? "");
  };

  const copyToClipboard = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text);
      toast("Copied install command", "success");
    } catch {
      toast("Copy failed", "error");
    }
  };

  const packages = data?.packages ?? [];
  const filteredPackages =
    typeFilter === "all"
      ? packages
      : packages.filter((p) => p.package_type === typeFilter);

  const prodCount = packages.filter((p) => p.package_type === "prod").length;
  const devCount = packages.filter((p) => p.package_type === "dev").length;

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Package size={18} />
            Package Manager
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <form
            onSubmit={async (e) => {
              e.preventDefault();
              await onSavePackageManager(managerDraft.trim());
            }}
            className="flex flex-wrap items-center gap-2"
          >
            <div className="min-w-[14rem] flex-1">
              <Input
                aria-label="Package manager"
                list="package-manager-options"
                placeholder="e.g. npm, pnpm, uv, poetry, cargo, go..."
                value={managerDraft}
                onChange={(e) => setManagerDraft(e.target.value)}
              />
              <datalist id="package-manager-options">
                {PACKAGE_MANAGERS.map((pm) => (
                  <option key={pm} value={pm} />
                ))}
              </datalist>
            </div>
            <Button type="submit" disabled={savingPackageManager}>
              {savingPackageManager ? "Saving…" : "Save manager"}
            </Button>
          </form>

          <div className="flex flex-wrap items-center gap-1.5">
            <span className="text-xs text-fg-soft">Presets:</span>
            {["npm", "pnpm", "yarn", "bun", "uv", "pip", "poetry", "cargo", "go"].map(
              (preset) => (
                <button
                  key={preset}
                  type="button"
                  onClick={() => setManagerDraft(preset)}
                  className={`rounded-md border px-2 py-0.5 font-mono text-xs transition-colors ${
                    managerDraft.trim().toLowerCase() === preset
                      ? "border-primary bg-primary/15 text-primary font-semibold"
                      : "border-border bg-surface-alt text-fg-soft hover:text-fg"
                  }`}
                >
                  {preset}
                </button>
              ),
            )}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-wrap items-center justify-between gap-2">
          <div>
            <CardTitle>Packages ({packages.length})</CardTitle>
            {packages.length > 0 && (
              <p className="mt-0.5 text-xs text-fg-soft">
                {prodCount} prod · {devCount} dev
                {packages.length - prodCount - devCount > 0
                  ? ` · ${packages.length - prodCount - devCount} other`
                  : ""}
              </p>
            )}
          </div>
          {packages.length > 0 && (
            <div className="flex items-center gap-1.5">
              <span className="text-xs text-fg-soft">Filter:</span>
              <Select
                aria-label="Filter packages by type"
                value={typeFilter}
                onChange={(e) => setTypeFilter(e.target.value as PackageType | "all")}
                className="w-36 py-1 text-xs"
              >
                <option value="all">All types ({packages.length})</option>
                {PACKAGE_TYPES.map((t) => (
                  <option key={t} value={t}>
                    {PACKAGE_TYPE_LABELS[t]}
                  </option>
                ))}
              </Select>
            </div>
          )}
        </CardHeader>
        <CardContent className="space-y-4">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              if (name.trim()) createMut.mutate();
            }}
            className="space-y-2 rounded-md border border-border bg-surface-alt/50 p-3"
          >
            <div className="grid gap-2 md:grid-cols-[2fr_1fr_1fr_auto]">
              <Input
                placeholder="Package name (e.g. fastapi, react)"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="font-mono"
              />
              <Input
                placeholder="Version (e.g. ^18.3.0)"
                value={version}
                onChange={(e) => setVersion(e.target.value)}
                className="font-mono"
              />
              <Select
                aria-label="Package type"
                value={packageType}
                onChange={(e) => setPackageType(e.target.value as PackageType)}
              >
                {PACKAGE_TYPES.map((t) => (
                  <option key={t} value={t}>
                    {PACKAGE_TYPE_LABELS[t]} ({t})
                  </option>
                ))}
              </Select>
              <Button type="submit" disabled={createMut.isPending}>
                Add package
              </Button>
            </div>
            <Input
              placeholder="Details / purpose (optional, e.g. HTTP client for async API calls)"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
            />
          </form>

          {isLoading && <LoadingState />}
          {data && filteredPackages.length === 0 && (
            <EmptyState
              title={packages.length === 0 ? "No packages tracked" : "No matching packages"}
              description={
                packages.length === 0
                  ? "Document key libraries, versions, and why this project uses them."
                  : "Try selecting a different dependency type filter."
              }
            />
          )}

          <ul className="divide-y divide-border">
            {filteredPackages.map((pkg) => {
              const isEditing = editingId === pkg.id;
              const installCmd = buildInstallCommand(
                savedManager || managerDraft || null,
                pkg.name,
                pkg.version,
                pkg.package_type,
              );

              if (isEditing) {
                return (
                  <li key={pkg.id} className="space-y-2 py-3">
                    <div className="grid gap-2 md:grid-cols-[2fr_1fr_1fr_auto]">
                      <Input
                        aria-label="Edit package name"
                        value={editName}
                        onChange={(e) => setEditName(e.target.value)}
                        className="font-mono"
                      />
                      <Input
                        aria-label="Edit package version"
                        placeholder="Version"
                        value={editVersion}
                        onChange={(e) => setEditVersion(e.target.value)}
                        className="font-mono"
                      />
                      <Select
                        aria-label="Edit package type"
                        value={editType}
                        onChange={(e) => setEditType(e.target.value as PackageType)}
                      >
                        {PACKAGE_TYPES.map((t) => (
                          <option key={t} value={t}>
                            {PACKAGE_TYPE_LABELS[t]} ({t})
                          </option>
                        ))}
                      </Select>
                      <div className="flex items-center gap-1">
                        <Button
                          type="button"
                          size="sm"
                          onClick={() => {
                            if (editName.trim()) updateMut.mutate(pkg.id);
                          }}
                          disabled={updateMut.isPending}
                          aria-label="Save package"
                        >
                          <Check size={14} /> Save
                        </Button>
                        <Button
                          type="button"
                          variant="ghost"
                          size="sm"
                          onClick={() => setEditingId(null)}
                          aria-label="Cancel edit"
                        >
                          <X size={14} />
                        </Button>
                      </div>
                    </div>
                    <Input
                      aria-label="Edit package description"
                      placeholder="Details / purpose"
                      value={editDescription}
                      onChange={(e) => setEditDescription(e.target.value)}
                    />
                  </li>
                );
              }

              return (
                <li
                  key={pkg.id}
                  className="flex flex-wrap items-start justify-between gap-3 py-3"
                >
                  <div className="min-w-0 flex-1 space-y-1">
                    <div className="flex flex-wrap items-center gap-2">
                      <span className="font-mono text-sm font-semibold text-fg">
                        {pkg.name}
                      </span>
                      {pkg.version && (
                        <code className="rounded bg-surface-alt px-1.5 py-0.5 font-mono text-xs text-fg-soft">
                          {pkg.version}
                        </code>
                      )}
                      <span
                        className={`rounded-full border px-2 py-0.5 text-xs font-medium ${TYPE_BADGE_CLASSES[pkg.package_type]}`}
                      >
                        {pkg.package_type}
                      </span>
                    </div>
                    {pkg.description && (
                      <p className="text-sm text-fg-soft">{pkg.description}</p>
                    )}
                    <div className="text-xs text-muted">
                      <code className="font-mono">{installCmd}</code>
                    </div>
                  </div>
                  <div className="flex items-center gap-1">
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => copyToClipboard(installCmd)}
                      title={`Copy: ${installCmd}`}
                      aria-label={`Copy install command for ${pkg.name}`}
                    >
                      <Copy size={14} />
                    </Button>
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => startEdit(pkg)}
                      aria-label={`Edit ${pkg.name}`}
                    >
                      <Edit3 size={14} />
                    </Button>
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => deleteMut.mutate(pkg.id)}
                      aria-label={`Delete ${pkg.name}`}
                    >
                      <Trash2 size={14} />
                    </Button>
                  </div>
                </li>
              );
            })}
          </ul>
        </CardContent>
      </Card>
    </div>
  );
}
