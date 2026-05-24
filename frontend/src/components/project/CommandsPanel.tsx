import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Copy, Trash2 } from "lucide-react";
import { api } from "@/lib/api/endpoints";
import { qk } from "@/lib/api/keys";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { LoadingState, EmptyState } from "@/components/ui/Empty";
import { useToast } from "@/components/Toast";

export function CommandsPanel({ projectId }: { projectId: number }) {
  const [label, setLabel] = useState("");
  const [command, setCommand] = useState("");
  const qc = useQueryClient();
  const { toast } = useToast();

  const { data, isLoading } = useQuery({
    queryKey: qk.commands(projectId),
    queryFn: () => api.listCommands(projectId),
  });

  const createMut = useMutation({
    mutationFn: () => api.createCommand(projectId, { label, command }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: qk.commands(projectId) });
      setLabel("");
      setCommand("");
    },
    onError: (e) => toast(`Add failed: ${(e as Error).message}`, "error"),
  });

  const deleteMut = useMutation({
    mutationFn: (id: number) => api.deleteCommand(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: qk.commands(projectId) }),
  });

  const copyToClipboard = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text);
      toast("Copied to clipboard", "success");
    } catch {
      toast("Copy failed", "error");
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Commands</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            if (label.trim() && command.trim()) createMut.mutate();
          }}
          className="grid gap-2 md:grid-cols-[1fr_2fr_auto]"
        >
          <Input
            placeholder="Label (e.g. Run dev)"
            value={label}
            onChange={(e) => setLabel(e.target.value)}
          />
          <Input
            placeholder="Command (e.g. uv run web)"
            value={command}
            onChange={(e) => setCommand(e.target.value)}
            className="font-mono"
          />
          <Button type="submit" disabled={createMut.isPending}>
            Add
          </Button>
        </form>

        {isLoading && <LoadingState />}
        {data && data.commands.length === 0 && (
          <EmptyState title="No commands" description="Stash common dev shortcuts." />
        )}

        <ul className="divide-y divide-border">
          {data?.commands.map((c) => (
            <li key={c.id} className="flex items-center gap-3 py-2">
              <div className="w-32 truncate text-sm font-medium">{c.label}</div>
              <code className="flex-1 truncate rounded bg-surface-alt px-2 py-1 font-mono text-xs">
                {c.command}
              </code>
              <Button
                variant="ghost"
                size="icon"
                onClick={() => copyToClipboard(c.command)}
                aria-label="Copy"
              >
                <Copy size={14} />
              </Button>
              <Button
                variant="ghost"
                size="icon"
                onClick={() => deleteMut.mutate(c.id)}
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
