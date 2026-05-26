import { useMemo } from "react";
import { useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  type Edge,
  type Node,
  MarkerType,
} from "reactflow";
import { api } from "@/lib/api/endpoints";
import { qk } from "@/lib/api/keys";
import { Card, CardContent } from "@/components/ui/Card";
import { LoadingState, ErrorState, EmptyState } from "@/components/ui/Empty";
import { useTheme } from "@/components/ThemeProvider";
import type { ProjectStatus } from "@/lib/api/types";

const statusColors: Record<ProjectStatus, string> = {
  idea: "#F59E0B",
  active: "#10B981",
  paused: "#6B7280",
  archived: "#9CA3AF",
};

export default function Graph() {
  const navigate = useNavigate();
  const { themeMode } = useTheme();
  const { data, isLoading, error } = useQuery({
    queryKey: qk.graph,
    queryFn: api.graph,
  });

  const { nodes, edges } = useMemo<{ nodes: Node[]; edges: Edge[] }>(() => {
    if (!data) return { nodes: [], edges: [] };
    // Simple radial layout: spread nodes around a circle.
    const count = data.nodes.length || 1;
    const radius = Math.max(220, count * 35);
    const flowNodes: Node[] = data.nodes.map((n, i) => {
      const angle = (i / count) * Math.PI * 2;
      return {
        id: String(n.id),
        position: {
          x: Math.cos(angle) * radius,
          y: Math.sin(angle) * radius,
        },
        data: { label: n.label, status: n.status },
        style: {
          background: themeMode === "dark" ? "#121826" : "#FFFFFF",
          color: themeMode === "dark" ? "#F3F4F6" : "#111827",
          border: `2px solid ${statusColors[n.status]}`,
          borderRadius: 8,
          padding: "8px 12px",
          fontSize: 12,
          fontWeight: 500,
        },
      };
    });
    const flowEdges: Edge[] = data.edges.map((e, i) => ({
      id: `e-${i}-${e.source}-${e.target}`,
      source: String(e.source),
      target: String(e.target),
      label: e.relationship_type,
      type: "default",
      animated: e.relationship_type === "depends_on",
      style: {
        stroke: e.is_inferred
          ? themeMode === "dark"
            ? "#7B8496"
            : "#9CA3AF"
          : "#60A5FA",
        strokeDasharray: e.is_inferred ? "4 4" : undefined,
      },
      labelStyle: {
        fontSize: 10,
        fill: themeMode === "dark" ? "#A8B0BF" : "#6B7280",
      },
      markerEnd: { type: MarkerType.ArrowClosed },
    }));
    return { nodes: flowNodes, edges: flowEdges };
  }, [data, themeMode]);

  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Graph</h1>
        <p className="mt-1 text-fg-soft">
          Project relationships and inferred connections via shared tags.
        </p>
      </div>

      {isLoading && <LoadingState />}
      {error && <ErrorState error={error} />}
      {data && data.nodes.length === 0 && (
        <EmptyState
          title="No projects to graph yet"
          description="Add projects and relationships to see them visualized here."
        />
      )}

      {data && data.nodes.length > 0 && (
        <Card>
          <CardContent className="h-[70vh] p-0">
            <ReactFlow
              nodes={nodes}
              edges={edges}
              onNodeClick={(_, node) => navigate(`/projects/${node.id}`)}
              fitView
              fitViewOptions={{ padding: 0.2 }}
              proOptions={{ hideAttribution: true }}
            >
              <Background gap={20} />
              <MiniMap pannable zoomable />
              <Controls />
            </ReactFlow>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
