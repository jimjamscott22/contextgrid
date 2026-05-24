import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ExternalLink, Trash2 } from "lucide-react";
import { api } from "@/lib/api/endpoints";
import { qk } from "@/lib/api/keys";
import { LINK_TYPES, type LinkType } from "@/lib/api/types";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Input, Select } from "@/components/ui/Input";
import { LoadingState, EmptyState } from "@/components/ui/Empty";
import { useToast } from "@/components/Toast";

export function LinksPanel({ projectId }: { projectId: number }) {
  const [title, setTitle] = useState("");
  const [url, setUrl] = useState("");
  const [linkType, setLinkType] = useState<LinkType>("other");
  const { toast } = useToast();
  const qc = useQueryClient();

  const { data, isLoading } = useQuery({
    queryKey: qk.links(projectId),
    queryFn: () => api.listLinks(projectId),
  });

  const createMut = useMutation({
    mutationFn: () =>
      api.createLink(projectId, { title, url, link_type: linkType }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: qk.links(projectId) });
      setTitle("");
      setUrl("");
      setLinkType("other");
    },
    onError: (e) => toast(`Add link failed: ${(e as Error).message}`, "error"),
  });

  const deleteMut = useMutation({
    mutationFn: (id: number) => api.deleteLink(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: qk.links(projectId) }),
  });

  return (
    <Card>
      <CardHeader>
        <CardTitle>Links</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            if (title.trim() && url.trim()) createMut.mutate();
          }}
          className="grid gap-2 md:grid-cols-[2fr_3fr_1fr_auto]"
        >
          <Input
            placeholder="Title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
          />
          <Input
            placeholder="https://..."
            value={url}
            onChange={(e) => setUrl(e.target.value)}
          />
          <Select
            value={linkType}
            onChange={(e) => setLinkType(e.target.value as LinkType)}
          >
            {LINK_TYPES.map((t) => (
              <option key={t} value={t}>
                {t}
              </option>
            ))}
          </Select>
          <Button type="submit" disabled={createMut.isPending}>
            Add
          </Button>
        </form>

        {isLoading && <LoadingState />}
        {data && data.links.length === 0 && (
          <EmptyState title="No links" description="Docs, dashboards, repos, deploys..." />
        )}

        <ul className="divide-y divide-border">
          {data?.links.map((l) => (
            <li key={l.id} className="flex items-center gap-3 py-2">
              <span className="cg-badge">{l.link_type}</span>
              <a
                href={l.url}
                target="_blank"
                rel="noopener noreferrer"
                className="flex-1 truncate text-fg no-underline hover:text-primary"
              >
                {l.title}
                <ExternalLink size={12} className="ml-1 inline" />
              </a>
              <Button
                variant="ghost"
                size="icon"
                onClick={() => deleteMut.mutate(l.id)}
                aria-label="Delete"
              >
                <Trash2 size={14} />
              </Button>
            </li>
          ))}
        </ul>
      </CardContent>
    </Card>
  );
}
