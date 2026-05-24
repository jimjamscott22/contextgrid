import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { X } from "lucide-react";
import { api } from "@/lib/api/endpoints";
import { qk } from "@/lib/api/keys";
import { Input } from "@/components/ui/Input";
import { useToast } from "@/components/Toast";

export function ProjectTagsPanel({ projectId }: { projectId: number }) {
  const [newTag, setNewTag] = useState("");
  const qc = useQueryClient();
  const { toast } = useToast();

  const tagsQ = useQuery({
    queryKey: qk.projectTags(projectId),
    queryFn: () => api.listProjectTags(projectId),
  });

  const addMut = useMutation({
    mutationFn: (name: string) => api.addTag(projectId, name),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: qk.projectTags(projectId) });
      qc.invalidateQueries({ queryKey: qk.tags });
      setNewTag("");
    },
    onError: (e) => toast(`Add tag failed: ${(e as Error).message}`, "error"),
  });

  const removeMut = useMutation({
    mutationFn: (name: string) => api.removeTag(projectId, name),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: qk.projectTags(projectId) });
      qc.invalidateQueries({ queryKey: qk.tags });
    },
    onError: (e) => toast(`Remove tag failed: ${(e as Error).message}`, "error"),
  });

  return (
    <div>
      <div className="text-xs font-semibold uppercase tracking-wide text-fg-soft">
        Tags
      </div>
      <div className="mt-2 flex flex-wrap items-center gap-2">
        {(tagsQ.data ?? []).map((t) => (
          <span
            key={t.name}
            className="inline-flex items-center gap-1 rounded-full border border-border bg-surface-alt px-2 py-0.5 text-xs"
          >
            {t.name}
            <button
              type="button"
              onClick={() => removeMut.mutate(t.name)}
              className="text-fg-soft hover:text-danger"
              aria-label={`Remove tag ${t.name}`}
            >
              <X size={12} />
            </button>
          </span>
        ))}
        <form
          onSubmit={(e) => {
            e.preventDefault();
            if (newTag.trim()) addMut.mutate(newTag.trim());
          }}
          className="flex items-center gap-2"
        >
          <Input
            value={newTag}
            onChange={(e) => setNewTag(e.target.value)}
            placeholder="add tag..."
            className="h-7 w-32 text-xs"
          />
        </form>
      </div>
    </div>
  );
}
