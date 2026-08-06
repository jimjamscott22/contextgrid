import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api/endpoints";
import { qk } from "@/lib/api/keys";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { LoadingState, ErrorState } from "@/components/ui/Empty";
import { Mermaid } from "@/components/Mermaid";
import { InteractiveMindmap } from "@/components/project/InteractiveMindmap";
import { Move, FileCode } from "lucide-react";

export default function Diagrams() {
  const [viewMode, setViewMode] = useState<"interactive" | "mermaid">("interactive");

  const mermaidQuery = useQuery({
    queryKey: qk.overviewMermaid,
    queryFn: api.overviewMermaid,
  });

  const graphQuery = useQuery({
    queryKey: qk.graph,
    queryFn: api.graph,
  });

  const isLoading = mermaidQuery.isLoading || graphQuery.isLoading;
  const error = mermaidQuery.error || graphQuery.error;

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Diagrams &amp; Workspace Mindmap</h1>
          <p className="mt-1 text-fg-soft">
            Interactive, editable node diagram and auto-generated mindmap overview.
          </p>
        </div>

        {/* View Mode Switcher */}
        <div className="inline-flex rounded-lg border border-border bg-surface-alt p-1 shadow-sm">
          <button
            onClick={() => setViewMode("interactive")}
            className={`inline-flex items-center gap-1.5 rounded-md px-3 py-1.5 text-xs font-semibold transition-all ${
              viewMode === "interactive"
                ? "bg-surface text-primary shadow-sm"
                : "text-fg-soft hover:text-fg"
            }`}
          >
            <Move size={14} /> Interactive Studio
          </button>
          <button
            onClick={() => setViewMode("mermaid")}
            className={`inline-flex items-center gap-1.5 rounded-md px-3 py-1.5 text-xs font-semibold transition-all ${
              viewMode === "mermaid"
                ? "bg-surface text-primary shadow-sm"
                : "text-fg-soft hover:text-fg"
            }`}
          >
            <FileCode size={14} /> Static Mermaid
          </button>
        </div>
      </div>

      {isLoading && <LoadingState />}
      {error && <ErrorState error={error} />}

      {!isLoading && !error && (
        <>
          {viewMode === "interactive" ? (
            <Card className="p-2">
              <InteractiveMindmap initialData={graphQuery.data} />
            </Card>
          ) : (
            mermaidQuery.data && (
              <Card>
                <CardHeader>
                  <CardTitle>Workspace overview ({mermaidQuery.data.diagram_type})</CardTitle>
                </CardHeader>
                <CardContent>
                  <Mermaid chart={mermaidQuery.data.diagram} />
                  <details className="mt-4">
                    <summary className="cursor-pointer text-xs text-fg-soft">
                      Show source
                    </summary>
                    <pre className="mt-2 overflow-x-auto rounded-md bg-surface-alt p-3 text-xs">
                      {mermaidQuery.data.diagram}
                    </pre>
                  </details>
                </CardContent>
              </Card>
            )
          )}
        </>
      )}
    </div>
  );
}

