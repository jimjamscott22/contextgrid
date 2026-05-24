import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { CheckCircle2, Circle, Trash2 } from "lucide-react";
import { api } from "@/lib/api/endpoints";
import { qk } from "@/lib/api/keys";
import { NOTE_TYPES, type NoteType, type NoteStatus } from "@/lib/api/types";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Select, Textarea } from "@/components/ui/Input";
import { Markdown } from "@/components/Markdown";
import { LoadingState, ErrorState, EmptyState } from "@/components/ui/Empty";
import { useToast } from "@/components/Toast";
import { relativeTime } from "@/lib/format";

export function NotesPanel({ projectId }: { projectId: number }) {
  const [content, setContent] = useState("");
  const [noteType, setNoteType] = useState<NoteType>("log");
  const qc = useQueryClient();
  const { toast } = useToast();

  const { data, isLoading, error } = useQuery({
    queryKey: qk.notes(projectId),
    queryFn: () => api.listNotes(projectId),
  });

  const createMut = useMutation({
    mutationFn: () => api.createNote(projectId, content, noteType),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: qk.notes(projectId) });
      qc.invalidateQueries({ queryKey: ["tasks"] });
      setContent("");
    },
    onError: (e) => toast(`Add note failed: ${(e as Error).message}`, "error"),
  });

  const statusMut = useMutation({
    mutationFn: ({ id, status }: { id: number; status: NoteStatus }) =>
      api.setNoteStatus(id, status),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: qk.notes(projectId) });
      qc.invalidateQueries({ queryKey: ["tasks"] });
    },
  });

  const deleteMut = useMutation({
    mutationFn: (id: number) => api.deleteNote(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: qk.notes(projectId) });
      qc.invalidateQueries({ queryKey: ["tasks"] });
    },
  });

  return (
    <Card>
      <CardHeader>
        <CardTitle>Notes & log</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            if (content.trim()) createMut.mutate();
          }}
          className="space-y-2"
        >
          <Textarea
            placeholder="Add a note... (markdown supported)"
            value={content}
            onChange={(e) => setContent(e.target.value)}
            rows={3}
          />
          <div className="flex items-center justify-between gap-2">
            <Select
              value={noteType}
              onChange={(e) => setNoteType(e.target.value as NoteType)}
              className="w-40"
            >
              {NOTE_TYPES.map((t) => (
                <option key={t} value={t}>
                  {t}
                </option>
              ))}
            </Select>
            <Button type="submit" disabled={!content.trim() || createMut.isPending}>
              Add note
            </Button>
          </div>
        </form>

        {isLoading && <LoadingState />}
        {error && <ErrorState error={error} />}
        {data && data.notes.length === 0 && (
          <EmptyState
            title="No notes yet"
            description="Capture progress, ideas, blockers, or reflections."
          />
        )}

        <ul className="divide-y divide-border">
          {data?.notes.map((n) => (
            <li key={n.id} className="flex items-start gap-3 py-3">
              <button
                type="button"
                onClick={() =>
                  statusMut.mutate({
                    id: n.id,
                    status: n.task_status === "completed" ? "active" : "completed",
                  })
                }
                className="mt-1 text-fg-soft hover:text-success"
                aria-label={n.task_status === "completed" ? "Mark active" : "Mark completed"}
              >
                {n.task_status === "completed" ? (
                  <CheckCircle2 size={16} className="text-success" />
                ) : (
                  <Circle size={16} />
                )}
              </button>
              <div className="min-w-0 flex-1">
                <div className="flex items-center gap-2 text-xs text-fg-soft">
                  <span className="cg-badge">{n.note_type}</span>
                  <span>{relativeTime(n.created_at)}</span>
                  {n.task_status !== "active" && (
                    <span className="cg-badge">{n.task_status}</span>
                  )}
                </div>
                <div className="mt-1">
                  <Markdown source={n.content} />
                </div>
              </div>
              <Button
                variant="ghost"
                size="icon"
                onClick={() => {
                  if (confirm("Delete this note?")) deleteMut.mutate(n.id);
                }}
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
