import { useEffect, useState, type FormEvent } from "react";
import { Button } from "@/components/ui/Button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { Textarea } from "@/components/ui/Input";
import {
  classifyTree,
  FOLDER_STRUCTURE_MAX_LENGTH,
  type TreeKind,
} from "@/lib/folderTree";

const KIND_CLASS: Record<TreeKind, string> = {
  folder: "text-warning",
  file: "text-success",
  plain: "text-fg",
};

interface FolderStructurePanelProps {
  saved: string | null;
  imageUrl: string | null;
  onSave: (value: string) => Promise<unknown> | void;
  saving?: boolean;
}

/**
 * Colored preview of a saved folder listing.
 * Folder names, file names, and tree marks use separate theme colors.
 */
export function FolderTreePreview({ source }: { source: string }) {
  const lines = classifyTree(source);
  return (
    <pre
      aria-label="Folder structure preview"
      className="overflow-x-auto rounded-md border border-border bg-surface-alt p-3 font-mono text-sm leading-relaxed"
    >
      {lines.map((line, index) => (
        <div key={index}>
          {line.glyphs ? <span className="text-muted">{line.glyphs}</span> : null}
          <span data-kind={line.kind} className={KIND_CLASS[line.kind]}>
            {line.name || "\u00a0"}
          </span>
        </div>
      ))}
    </pre>
  );
}

/**
 * Paste, replace, and clear a project's folder listing.
 * The colored preview follows the saved text, not the text box.
 */
export function FolderStructurePanel({
  saved,
  imageUrl,
  onSave,
  saving = false,
}: FolderStructurePanelProps) {
  const savedText = saved ?? "";
  const [draft, setDraft] = useState(savedText);
  const tooLong = draft.length > FOLDER_STRUCTURE_MAX_LENGTH;

  useEffect(() => {
    setDraft(savedText);
  }, [savedText]);

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    if (tooLong || saving) return;
    const next = draft.trim() ? draft.trim() : "";
    await onSave(next);
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Folder structure</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <form onSubmit={submit} className="space-y-2">
          <label htmlFor="folder-structure" className="cg-label">
            Folder tree
          </label>
          <Textarea
            id="folder-structure"
            value={draft}
            onChange={(event) => setDraft(event.target.value)}
            rows={10}
            spellCheck={false}
            placeholder={"Paste the output of tree, or type a folder structure"}
            className="font-mono text-sm"
          />
          {tooLong && (
            <p className="text-sm text-danger" role="alert">
              Folder tree must be {FOLDER_STRUCTURE_MAX_LENGTH.toLocaleString()}{" "}
              characters or fewer.
            </p>
          )}
          <Button type="submit" disabled={saving || tooLong}>
            {saving ? "Saving…" : "Save"}
          </Button>
        </form>
        {savedText.trim() ? <FolderTreePreview source={savedText} /> : null}
        {imageUrl ? (
          <img
            src={imageUrl}
            alt="Folder structure diagram"
            className="max-w-full rounded-md border border-border"
          />
        ) : null}
      </CardContent>
    </Card>
  );
}
