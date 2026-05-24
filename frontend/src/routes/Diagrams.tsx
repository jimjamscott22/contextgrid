import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api/endpoints";
import { qk } from "@/lib/api/keys";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { LoadingState, ErrorState } from "@/components/ui/Empty";
import { Mermaid } from "@/components/Mermaid";

export default function Diagrams() {
  const { data, isLoading, error } = useQuery({
    queryKey: qk.overviewMermaid,
    queryFn: api.overviewMermaid,
  });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Diagrams</h1>
        <p className="mt-1 text-fg-soft">
          Auto-generated Mermaid diagram of your workspace.
        </p>
      </div>

      {isLoading && <LoadingState />}
      {error && <ErrorState error={error} />}
      {data && (
        <Card>
          <CardHeader>
            <CardTitle>Workspace overview ({data.diagram_type})</CardTitle>
          </CardHeader>
          <CardContent>
            <Mermaid chart={data.diagram} />
            <details className="mt-4">
              <summary className="cursor-pointer text-xs text-fg-soft">
                Show source
              </summary>
              <pre className="mt-2 overflow-x-auto rounded-md bg-surface-alt p-3 text-xs">
                {data.diagram}
              </pre>
            </details>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
