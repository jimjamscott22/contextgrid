import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Plus, Trash2 } from "lucide-react";
import { api } from "@/lib/api/endpoints";
import { qk } from "@/lib/api/keys";
import {
  PROJECT_STATUSES,
  PROJECT_TYPES,
  SCOPE_SIZES,
  projectTypeLabel,
  type Template,
} from "@/lib/api/types";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Input, Select, Textarea } from "@/components/ui/Input";
import { Dialog } from "@/components/ui/Dialog";
import { LoadingState, ErrorState, EmptyState } from "@/components/ui/Empty";
import { useToast } from "@/components/Toast";

export default function Templates() {
  const [createOpen, setCreateOpen] = useState(false);
  const { toast } = useToast();
  const qc = useQueryClient();

  const { data, isLoading, error } = useQuery({
    queryKey: qk.templates,
    queryFn: api.listTemplates,
  });

  const deleteMut = useMutation({
    mutationFn: (id: number) => api.deleteTemplate(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: qk.templates });
      toast("Template deleted", "success");
    },
    onError: (e) => toast(`Delete failed: ${(e as Error).message}`, "error"),
  });

  return (
    <div className="space-y-6">
      <div className="flex items-end justify-between gap-3">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Templates</h1>
          <p className="mt-1 text-fg-soft">
            Reusable starting points for new projects.
          </p>
        </div>
        <Button onClick={() => setCreateOpen(true)}>
          <Plus size={16} /> New template
        </Button>
      </div>

      {isLoading && <LoadingState />}
      {error && <ErrorState error={error} />}
      {data && data.templates.length === 0 && (
        <EmptyState
          title="No templates yet"
          description="Create a template to bootstrap projects with sensible defaults."
        />
      )}

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {data?.templates.map((t) => (
          <Card key={t.id}>
            <CardHeader className="flex flex-row items-start justify-between">
              <CardTitle>{t.name}</CardTitle>
              <Button
                variant="ghost"
                size="icon"
                onClick={() => {
                  if (confirm(`Delete template "${t.name}"?`)) {
                    deleteMut.mutate(t.id);
                  }
                }}
                aria-label="Delete"
              >
                <Trash2 size={16} />
              </Button>
            </CardHeader>
            <CardContent className="space-y-2">
              {t.description && (
                <p className="text-sm text-fg-soft">{t.description}</p>
              )}
              <div className="flex flex-wrap gap-1.5">
                <span className="cg-badge">{t.default_status}</span>
                {t.default_project_type && (
                  <span className="cg-badge">
                    {projectTypeLabel(t.default_project_type)}
                  </span>
                )}
                {t.default_primary_language && (
                  <span className="cg-badge">{t.default_primary_language}</span>
                )}
                {t.default_scope_size && (
                  <span className="cg-badge">{t.default_scope_size}</span>
                )}
              </div>
              {t.default_tags && (
                <div className="text-xs text-fg-soft">tags: {t.default_tags}</div>
              )}
            </CardContent>
          </Card>
        ))}
      </div>

      <CreateTemplateDialog
        open={createOpen}
        onOpenChange={setCreateOpen}
        onCreated={() => qc.invalidateQueries({ queryKey: qk.templates })}
      />
    </div>
  );
}

function CreateTemplateDialog({
  open,
  onOpenChange,
  onCreated,
}: {
  open: boolean;
  onOpenChange: (v: boolean) => void;
  onCreated: () => void;
}) {
  const [form, setForm] = useState<Partial<Template>>({
    name: "",
    description: "",
    default_status: "idea",
    default_project_type: null,
    default_primary_language: "",
    default_stack: "",
    default_scope_size: null,
    default_learning_goal: "",
    default_tags: "",
  });
  const { toast } = useToast();
  const mut = useMutation({
    mutationFn: (data: Partial<Template>) => api.createTemplate(data),
    onSuccess: () => {
      toast("Template created", "success");
      onCreated();
      onOpenChange(false);
    },
    onError: (e) => toast(`Create failed: ${(e as Error).message}`, "error"),
  });

  return (
    <Dialog
      open={open}
      onOpenChange={onOpenChange}
      title="Create template"
      description="Define defaults for a new kind of project."
    >
      <form
        onSubmit={(e) => {
          e.preventDefault();
          mut.mutate({
            ...form,
            default_project_type: form.default_project_type || null,
            default_scope_size: form.default_scope_size || null,
          });
        }}
        className="space-y-4"
      >
        <Field label="Name">
          <Input
            required
            value={form.name ?? ""}
            onChange={(e) => setForm({ ...form, name: e.target.value })}
          />
        </Field>
        <Field label="Description">
          <Textarea
            rows={2}
            value={form.description ?? ""}
            onChange={(e) => setForm({ ...form, description: e.target.value })}
          />
        </Field>
        <div className="grid gap-3 md:grid-cols-2">
          <Field label="Default status">
            <Select
              value={form.default_status ?? "idea"}
              onChange={(e) =>
                setForm({ ...form, default_status: e.target.value as Template["default_status"] })
              }
            >
              {PROJECT_STATUSES.map((s) => (
                <option key={s} value={s}>
                  {s}
                </option>
              ))}
            </Select>
          </Field>
          <Field label="Default type">
            <Select
              value={form.default_project_type ?? ""}
              onChange={(e) =>
                setForm({
                  ...form,
                  default_project_type: (e.target.value || null) as Template["default_project_type"],
                })
              }
            >
              <option value="">—</option>
              {PROJECT_TYPES.map((s) => (
                <option key={s} value={s}>
                  {projectTypeLabel(s)}
                </option>
              ))}
            </Select>
          </Field>
          <Field label="Primary language">
            <Input
              value={form.default_primary_language ?? ""}
              onChange={(e) =>
                setForm({ ...form, default_primary_language: e.target.value })
              }
            />
          </Field>
          <Field label="Stack">
            <Input
              value={form.default_stack ?? ""}
              onChange={(e) => setForm({ ...form, default_stack: e.target.value })}
            />
          </Field>
          <Field label="Scope">
            <Select
              value={form.default_scope_size ?? ""}
              onChange={(e) =>
                setForm({
                  ...form,
                  default_scope_size: (e.target.value || null) as Template["default_scope_size"],
                })
              }
            >
              <option value="">—</option>
              {SCOPE_SIZES.map((s) => (
                <option key={s} value={s}>
                  {s}
                </option>
              ))}
            </Select>
          </Field>
          <Field label="Tags (comma sep.)">
            <Input
              value={form.default_tags ?? ""}
              onChange={(e) => setForm({ ...form, default_tags: e.target.value })}
            />
          </Field>
        </div>
        <Field label="Learning goal">
          <Textarea
            rows={2}
            value={form.default_learning_goal ?? ""}
            onChange={(e) => setForm({ ...form, default_learning_goal: e.target.value })}
          />
        </Field>
        <div className="flex justify-end gap-2">
          <Button type="button" variant="secondary" onClick={() => onOpenChange(false)}>
            Cancel
          </Button>
          <Button type="submit" disabled={mut.isPending}>
            {mut.isPending ? "Creating..." : "Create"}
          </Button>
        </div>
      </form>
    </Dialog>
  );
}

function Field({
  label,
  children,
}: {
  label: string;
  children: React.ReactNode;
}) {
  return (
    <label className="block space-y-1.5">
      <span className="cg-label">{label}</span>
      {children}
    </label>
  );
}
