import { useState } from "react";
import { Link } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Trash2, ArrowRight, ArrowLeft } from "lucide-react";
import { api } from "@/lib/api/endpoints";
import { qk } from "@/lib/api/keys";
import { RELATIONSHIP_TYPES, type RelationshipType } from "@/lib/api/types";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Select } from "@/components/ui/Input";
import { LoadingState, EmptyState } from "@/components/ui/Empty";
import { useToast } from "@/components/Toast";

export function RelationshipsPanel({ projectId }: { projectId: number }) {
  const [targetId, setTargetId] = useState<string>("");
  const [relType, setRelType] = useState<RelationshipType>("related_to");
  const qc = useQueryClient();
  const { toast } = useToast();

  const { data, isLoading } = useQuery({
    queryKey: qk.relationships(projectId),
    queryFn: () => api.listRelationships(projectId),
  });
  const projectsQ = useQuery({
    queryKey: qk.projects({ all: true }),
    queryFn: () => api.listProjects({ limit: 500, include_archived: true }),
  });

  const createMut = useMutation({
    mutationFn: () =>
      api.createRelationship(projectId, Number(targetId), relType),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: qk.relationships(projectId) });
      qc.invalidateQueries({ queryKey: qk.graph });
      setTargetId("");
    },
    onError: (e) => toast(`Add failed: ${(e as Error).message}`, "error"),
  });

  const deleteMut = useMutation({
    mutationFn: (id: number) => api.deleteRelationship(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: qk.relationships(projectId) });
      qc.invalidateQueries({ queryKey: qk.graph });
    },
  });

  const otherProjects =
    projectsQ.data?.projects.filter((p) => p.id !== projectId) ?? [];

  return (
    <Card>
      <CardHeader>
        <CardTitle>Relationships</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            if (targetId) createMut.mutate();
          }}
          className="grid gap-2 md:grid-cols-[2fr_1fr_auto]"
        >
          <Select value={targetId} onChange={(e) => setTargetId(e.target.value)}>
            <option value="">Select related project...</option>
            {otherProjects.map((p) => (
              <option key={p.id} value={p.id}>
                {p.name}
              </option>
            ))}
          </Select>
          <Select
            value={relType}
            onChange={(e) => setRelType(e.target.value as RelationshipType)}
          >
            {RELATIONSHIP_TYPES.map((r) => (
              <option key={r} value={r}>
                {r.replace("_", " ")}
              </option>
            ))}
          </Select>
          <Button type="submit" disabled={!targetId || createMut.isPending}>
            Link
          </Button>
        </form>

        {isLoading && <LoadingState />}
        {data && data.relationships.length === 0 && (
          <EmptyState title="No relationships" description="Connect related work." />
        )}

        <ul className="divide-y divide-border">
          {data?.relationships.map((r) => (
            <li key={r.id} className="flex items-center gap-3 py-2 text-sm">
              {r.direction === "outgoing" ? (
                <ArrowRight size={14} className="text-primary" />
              ) : (
                <ArrowLeft size={14} className="text-accent" />
              )}
              <span className="text-fg-soft capitalize">
                {r.relationship_type.replace("_", " ")}
              </span>
              <Link
                to={`/projects/${r.target_project_id}`}
                className="flex-1 truncate font-medium"
              >
                {r.target_project_name}
              </Link>
              {r.direction === "outgoing" && (
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => deleteMut.mutate(r.id)}
                  aria-label="Remove"
                >
                  <Trash2 size={14} />
                </Button>
              )}
            </li>
          ))}
        </ul>
      </CardContent>
    </Card>
  );
}
