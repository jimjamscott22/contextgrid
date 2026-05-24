import { useRef } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Trash2, Upload } from "lucide-react";
import { api } from "@/lib/api/endpoints";
import { qk } from "@/lib/api/keys";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { LoadingState, EmptyState } from "@/components/ui/Empty";
import { useToast } from "@/components/Toast";

export function ScreenshotsPanel({ projectId }: { projectId: number }) {
  const fileInput = useRef<HTMLInputElement>(null);
  const qc = useQueryClient();
  const { toast } = useToast();

  const { data, isLoading } = useQuery({
    queryKey: qk.screenshots(projectId),
    queryFn: () => api.listScreenshots(projectId),
  });

  const uploadMut = useMutation({
    mutationFn: (file: File) => api.uploadScreenshot(projectId, file),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: qk.screenshots(projectId) });
      toast("Uploaded", "success");
    },
    onError: (e) => toast(`Upload failed: ${(e as Error).message}`, "error"),
  });

  const deleteMut = useMutation({
    mutationFn: (filename: string) => api.deleteScreenshot(projectId, filename),
    onSuccess: () => qc.invalidateQueries({ queryKey: qk.screenshots(projectId) }),
  });

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle>Screenshots</CardTitle>
        <div>
          <input
            ref={fileInput}
            type="file"
            accept="image/*"
            className="hidden"
            onChange={(e) => {
              const file = e.target.files?.[0];
              if (file) uploadMut.mutate(file);
              e.target.value = "";
            }}
          />
          <Button
            variant="secondary"
            onClick={() => fileInput.current?.click()}
            disabled={uploadMut.isPending}
          >
            <Upload size={16} /> Upload
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        {isLoading && <LoadingState />}
        {data && data.screenshots.length === 0 && (
          <EmptyState
            title="No screenshots"
            description="Upload PNG/JPG snapshots of your project."
          />
        )}

        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {data?.screenshots.map((s) => (
            <figure
              key={s.filename}
              className="group relative overflow-hidden rounded-md border border-border bg-surface-alt"
            >
              <img src={s.url} alt={s.label} className="block w-full" />
              <figcaption className="flex items-center justify-between gap-2 border-t border-border p-2 text-xs text-fg-soft">
                <span className="truncate">{s.label}</span>
                <button
                  type="button"
                  onClick={() => {
                    if (confirm(`Delete ${s.filename}?`)) deleteMut.mutate(s.filename);
                  }}
                  className="text-fg-soft hover:text-danger"
                  aria-label="Delete"
                >
                  <Trash2 size={14} />
                </button>
              </figcaption>
            </figure>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
