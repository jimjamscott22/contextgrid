import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ApiError } from "@/lib/api/client";
import { Trash2 } from "lucide-react";
import { api } from "@/lib/api/endpoints";
import { qk } from "@/lib/api/keys";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Markdown } from "@/components/Markdown";
import { LoadingState, ErrorState, EmptyState } from "@/components/ui/Empty";
import { useToast } from "@/components/Toast";
import { formatDate } from "@/lib/format";

export function ReadmePanel({ projectId }: { projectId: number }) {
  const [source, setSource] = useState("");
  const qc = useQueryClient();
  const { toast } = useToast();

  const { data, isLoading, error } = useQuery({
    queryKey: qk.readme(projectId),
    queryFn: () => api.getReadme(projectId),
    retry: false,
  });

  const attachMut = useMutation({
    mutationFn: () => api.attachReadme(projectId, source),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: qk.readme(projectId) });
      toast("README attached", "success");
      setSource("");
    },
    onError: (e) => toast(`Attach failed: ${(e as Error).message}`, "error"),
  });
  const deleteMut = useMutation({
    mutationFn: () => api.deleteReadme(projectId),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: qk.readme(projectId) });
      toast("README removed", "success");
    },
  });

  const notFound = error instanceof ApiError && error.status === 404;

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle>README snapshot</CardTitle>
        {data && (
          <Button
            variant="ghost"
            size="icon"
            onClick={() => {
              if (confirm("Remove README snapshot?")) deleteMut.mutate();
            }}
            aria-label="Delete"
          >
            <Trash2 size={14} />
          </Button>
        )}
      </CardHeader>
      <CardContent className="space-y-4">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            if (source.trim()) attachMut.mutate();
          }}
          className="flex gap-2"
        >
          <Input
            placeholder="Path or URL to README (e.g. ./README.md or https://...)"
            value={source}
            onChange={(e) => setSource(e.target.value)}
          />
          <Button type="submit" disabled={!source.trim() || attachMut.isPending}>
            {data ? "Refresh" : "Attach"}
          </Button>
        </form>

        {isLoading && <LoadingState />}
        {error && !notFound && <ErrorState error={error} />}
        {notFound && (
          <EmptyState
            title="No README attached"
            description="Provide a path or URL above to snapshot a README."
          />
        )}
        {data && (
          <div>
            <div className="mb-3 flex items-center gap-3 text-xs text-fg-soft">
              {data.source_ref && <span>Source: {data.source_ref}</span>}
              <span>Fetched {formatDate(data.fetched_at)}</span>
            </div>
            <div className="rounded-md border border-border bg-surface-alt p-4">
              <Markdown source={data.content} />
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
