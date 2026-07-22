import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import {
  PROJECT_STATUSES,
  PROJECT_TYPES,
  SCOPE_SIZES,
  projectTypeLabel,
  type ProjectInput,
} from "@/lib/api/types";
import { Input, Select, Textarea } from "@/components/ui/Input";
import { Button } from "@/components/ui/Button";

const projectSchema = z.object({
  name: z.string().min(1, "Name is required").max(255),
  description: z.string().optional().nullable(),
  status: z.enum(["idea", "active", "paused", "archived"]),
  project_type: z.enum(PROJECT_TYPES).nullable().optional(),
  primary_language: z.string().nullable().optional(),
  stack: z.string().nullable().optional(),
  repo_url: z.string().nullable().optional(),
  local_path: z.string().nullable().optional(),
  scope_size: z.enum(["tiny", "medium", "long-haul"]).nullable().optional(),
  learning_goal: z.string().nullable().optional(),
  progress: z.coerce.number().int().min(0).max(100),
});

export type ProjectFormValues = z.infer<typeof projectSchema>;

interface ProjectFormProps {
  defaultValues?: Partial<ProjectFormValues>;
  onSubmit: (values: ProjectInput) => void | Promise<void>;
  submitting?: boolean;
  submitLabel?: string;
  onCancel?: () => void;
}

export function ProjectForm({
  defaultValues,
  onSubmit,
  submitting,
  submitLabel = "Save",
  onCancel,
}: ProjectFormProps) {
  const form = useForm<ProjectFormValues>({
    resolver: zodResolver(projectSchema),
    defaultValues: {
      name: "",
      description: "",
      status: "idea",
      project_type: null,
      primary_language: "",
      stack: "",
      repo_url: "",
      local_path: "",
      scope_size: null,
      learning_goal: "",
      progress: 0,
      ...defaultValues,
    },
  });

  const submit = form.handleSubmit(async (values) => {
    const cleaned: ProjectInput = {
      ...values,
      description: values.description || null,
      primary_language: values.primary_language || null,
      stack: values.stack || null,
      repo_url: values.repo_url || null,
      local_path: values.local_path || null,
      learning_goal: values.learning_goal || null,
      project_type: values.project_type || null,
      scope_size: values.scope_size || null,
    };
    await onSubmit(cleaned);
  });

  return (
    <form onSubmit={submit} className="space-y-4">
      <div className="grid gap-4 md:grid-cols-2">
        <Field label="Name" error={form.formState.errors.name?.message}>
          <Input {...form.register("name")} autoFocus />
        </Field>
        <Field label="Status">
          <Select {...form.register("status")}>
            {PROJECT_STATUSES.map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </Select>
        </Field>

        <Field label="Type">
          <Select
            {...form.register("project_type", {
              setValueAs: (v) => (v === "" ? null : v),
            })}
          >
            <option value="">—</option>
            {PROJECT_TYPES.map((s) => (
              <option key={s} value={s}>
                {projectTypeLabel(s)}
              </option>
            ))}
          </Select>
        </Field>
        <Field label="Scope">
          <Select
            {...form.register("scope_size", {
              setValueAs: (v) => (v === "" ? null : v),
            })}
          >
            <option value="">—</option>
            {SCOPE_SIZES.map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </Select>
        </Field>

        <Field label="Primary language">
          <Input {...form.register("primary_language")} placeholder="e.g. Python" />
        </Field>
        <Field label="Stack">
          <Input {...form.register("stack")} placeholder="e.g. FastAPI + React" />
        </Field>

        <Field label="Repo URL">
          <Input {...form.register("repo_url")} placeholder="https://..." />
        </Field>
        <Field label="Local path">
          <Input {...form.register("local_path")} placeholder="/home/you/code/..." />
        </Field>

        <Field label="Progress (%)" error={form.formState.errors.progress?.message}>
          <Input
            type="number"
            min={0}
            max={100}
            {...form.register("progress", { valueAsNumber: true })}
          />
        </Field>
      </div>

      <Field label="Description">
        <Textarea rows={3} {...form.register("description")} />
      </Field>

      <Field label="Learning goal">
        <Textarea rows={2} {...form.register("learning_goal")} />
      </Field>

      <div className="flex justify-end gap-2">
        {onCancel && (
          <Button type="button" variant="secondary" onClick={onCancel}>
            Cancel
          </Button>
        )}
        <Button type="submit" disabled={submitting}>
          {submitting ? "Saving..." : submitLabel}
        </Button>
      </div>
    </form>
  );
}

function Field({
  label,
  error,
  children,
}: {
  label: string;
  error?: string;
  children: React.ReactNode;
}) {
  return (
    <label className="block space-y-1.5">
      <span className="cg-label">{label}</span>
      {children}
      {error && <span className="block text-xs text-danger">{error}</span>}
    </label>
  );
}
