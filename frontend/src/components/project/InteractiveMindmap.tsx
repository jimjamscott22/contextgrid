import { useState, useCallback, useMemo, useEffect } from "react";
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  addEdge,
  type Connection,
  type Edge,
  type Node,
  MarkerType,
  Panel,
} from "reactflow";
import { Plus, RotateCcw, Save, Download, Sparkles, Move, Palette, Type } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { EditableNode, PRESET_COLORS, type CustomNodeData } from "./EditableNode";
import { useTheme } from "@/components/ThemeProvider";

const STORAGE_KEY = "contextgrid_mindmap_layout_v1";

const nodeTypes = {
  editableNode: EditableNode,
};

interface OverviewData {
  diagram_type?: string;
  diagram?: string;
  nodes?: Array<{ id: string | number; label: string; status?: string; type?: string }>;
  edges?: Array<{ source: string | number; target: string | number; label?: string }>;
}

interface InteractiveMindmapProps {
  initialData?: OverviewData;
}

export function InteractiveMindmap({ initialData }: InteractiveMindmapProps) {
  const { themeMode } = useTheme();
  const [nodes, setNodes, onNodesChange] = useNodesState<CustomNodeData>([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);
  const [isSaved, setIsSaved] = useState(false);

  // Helper to compute radial initial positions
  const buildInitialElements = useCallback(() => {
    const rawNodes = initialData?.nodes || [];
    const rawEdges = initialData?.edges || [];

    if (rawNodes.length === 0) {
      // Default fallback workspace mindmap
      const hubNode: Node<CustomNodeData> = {
        id: "hub-1",
        type: "editableNode",
        position: { x: 400, y: 300 },
        data: {
          label: "ContextGrid Workspace",
          isHub: true,
          nodeType: "hub",
          bgColor: "#1E40AF",
          borderColor: "#3B82F6",
          textColor: "#FFFFFF",
        },
      };

      const defaultNodes: Node<CustomNodeData>[] = [
        hubNode,
        {
          id: "node-active",
          type: "editableNode",
          position: { x: 400, y: 120 },
          data: {
            label: "Active Projects",
            status: "active",
            bgColor: "#DCFCE7",
            borderColor: "#22C55E",
            textColor: "#166534",
          },
        },
        {
          id: "node-ideas",
          type: "editableNode",
          position: { x: 620, y: 300 },
          data: {
            label: "Idea Backlog",
            status: "idea",
            bgColor: "#FEF08A",
            borderColor: "#EAB308",
            textColor: "#854D0E",
          },
        },
        {
          id: "node-paused",
          type: "editableNode",
          position: { x: 400, y: 480 },
          data: {
            label: "Paused Tasks",
            status: "paused",
            bgColor: "#F3E8FF",
            borderColor: "#A855F7",
            textColor: "#6B21A8",
          },
        },
        {
          id: "node-archived",
          type: "editableNode",
          position: { x: 180, y: 300 },
          data: {
            label: "Archived Notes",
            status: "archived",
            bgColor: "#F1F5F9",
            borderColor: "#64748B",
            textColor: "#334155",
          },
        },
      ];

      const defaultEdges: Edge[] = [
        { id: "e-hub-active", source: "hub-1", target: "node-active", markerEnd: { type: MarkerType.ArrowClosed } },
        { id: "e-hub-ideas", source: "hub-1", target: "node-ideas", markerEnd: { type: MarkerType.ArrowClosed } },
        { id: "e-hub-paused", source: "hub-1", target: "node-paused", markerEnd: { type: MarkerType.ArrowClosed } },
        { id: "e-hub-archived", source: "hub-1", target: "node-archived", markerEnd: { type: MarkerType.ArrowClosed } },
      ];

      return { initialNodes: defaultNodes, initialEdges: defaultEdges };
    }

    // Compute layout for incoming node graph
    const centerNodeId = String(rawNodes[0]?.id || "center");
    const count = Math.max(1, rawNodes.length - 1);
    const radius = Math.max(250, count * 35);

    const initialNodes: Node<CustomNodeData>[] = rawNodes.map((n, i) => {
      const idStr = String(n.id);
      const isHub = i === 0 || idStr === centerNodeId;

      let pos = { x: 400, y: 350 };
      if (!isHub) {
        const angle = ((i - 1) / count) * Math.PI * 2;
        pos = {
          x: 400 + Math.cos(angle) * radius,
          y: 350 + Math.sin(angle) * radius,
        };
      }

      // Default status preset color mapping
      let preset = PRESET_COLORS[0];
      if (n.status === "active") preset = PRESET_COLORS[1];
      else if (n.status === "paused") preset = PRESET_COLORS[2];
      else if (n.status === "archived") preset = PRESET_COLORS[5];
      else if (isHub) preset = { name: "Hub", bg: "#1D4ED8", border: "#3B82F6", text: "#FFFFFF" };

      return {
        id: idStr,
        type: "editableNode",
        position: pos,
        data: {
          label: n.label,
          status: n.status,
          isHub,
          bgColor: preset.bg,
          borderColor: preset.border,
          textColor: preset.text,
        },
      };
    });

    const initialEdges: Edge[] = rawEdges.map((e, idx) => ({
      id: `e-${idx}-${e.source}-${e.target}`,
      source: String(e.source),
      target: String(e.target),
      label: e.label,
      type: "smoothstep",
      animated: true,
      markerEnd: { type: MarkerType.ArrowClosed },
      style: { stroke: "#60A5FA", strokeWidth: 2 },
    }));

    return { initialNodes, initialEdges };
  }, [initialData]);

  // Handle label change callback
  const handleLabelChange = useCallback((id: string, newLabel: string) => {
    setNodes((nds) =>
      nds.map((node) => {
        if (node.id === id) {
          return {
            ...node,
            data: {
              ...node.data,
              label: newLabel,
            },
          };
        }
        return node;
      })
    );
  }, [setNodes]);

  // Handle color change callback
  const handleColorChange = useCallback(
    (id: string, bgColor: string, borderColor: string, textColor: string) => {
      setNodes((nds) =>
        nds.map((node) => {
          if (node.id === id) {
            return {
              ...node,
              data: {
                ...node.data,
                bgColor,
                borderColor,
                textColor,
              },
            };
          }
          return node;
        })
      );
    },
    [setNodes]
  );

  // Handle node delete callback
  const handleDeleteNode = useCallback(
    (id: string) => {
      setNodes((nds) => nds.filter((n) => n.id !== id));
      setEdges((eds) => eds.filter((e) => e.source !== id && e.target !== id));
      if (selectedNodeId === id) setSelectedNodeId(null);
    },
    [setNodes, setEdges, selectedNodeId]
  );

  // Bind node callbacks to node data
  const injectCallbacks = useCallback(
    (nodesList: Node<CustomNodeData>[]): Node<CustomNodeData>[] => {
      return nodesList.map((n) => ({
        ...n,
        data: {
          ...n.data,
          onLabelChange: handleLabelChange,
          onColorChange: handleColorChange,
          onDeleteNode: handleDeleteNode,
        },
      }));
    },
    [handleLabelChange, handleColorChange, handleDeleteNode]
  );

  // Initial load from localStorage or compute layout
  useEffect(() => {
    const savedState = localStorage.getItem(STORAGE_KEY);
    if (savedState) {
      try {
        const parsed = JSON.parse(savedState);
        if (parsed.nodes && parsed.nodes.length > 0) {
          setNodes(injectCallbacks(parsed.nodes));
          setEdges(parsed.edges || []);
          return;
        }
      } catch (err) {
        console.error("Failed to parse saved layout:", err);
      }
    }

    const { initialNodes, initialEdges } = buildInitialElements();
    setNodes(injectCallbacks(initialNodes));
    setEdges(initialEdges);
  }, [buildInitialElements, injectCallbacks, setNodes, setEdges]);

  // Connect edges on canvas
  const onConnect = useCallback(
    (params: Connection) => {
      setEdges((eds) =>
        addEdge(
          {
            ...params,
            type: "smoothstep",
            animated: true,
            markerEnd: { type: MarkerType.ArrowClosed },
            style: { stroke: "#60A5FA", strokeWidth: 2 },
          },
          eds
        )
      );
    },
    [setEdges]
  );

  // Add new custom node
  const handleAddNode = () => {
    const newId = `custom-node-${Date.now()}`;
    const preset = PRESET_COLORS[Math.floor(Math.random() * PRESET_COLORS.length)];
    const newNode: Node<CustomNodeData> = {
      id: newId,
      type: "editableNode",
      position: {
        x: 350 + (Math.random() * 100 - 50),
        y: 250 + (Math.random() * 100 - 50),
      },
      data: {
        label: "New Node",
        bgColor: preset.bg,
        borderColor: preset.border,
        textColor: preset.text,
        onLabelChange: handleLabelChange,
        onColorChange: handleColorChange,
        onDeleteNode: handleDeleteNode,
      },
    };
    setNodes((nds) => [...nds, newNode]);
    setSelectedNodeId(newId);
  };

  // Reset layout to default
  const handleResetLayout = () => {
    localStorage.removeItem(STORAGE_KEY);
    const { initialNodes, initialEdges } = buildInitialElements();
    setNodes(injectCallbacks(initialNodes));
    setEdges(initialEdges);
    setSelectedNodeId(null);
  };

  // Save current state to localStorage
  const handleSaveLayout = () => {
    const dataToSave = {
      nodes: nodes.map((n) => ({
        id: n.id,
        type: n.type,
        position: n.position,
        data: {
          label: n.data.label,
          status: n.data.status,
          isHub: n.data.isHub,
          bgColor: n.data.bgColor,
          borderColor: n.data.borderColor,
          textColor: n.data.textColor,
        },
      })),
      edges,
    };
    localStorage.setItem(STORAGE_KEY, JSON.stringify(dataToSave));
    setIsSaved(true);
    setTimeout(() => setIsSaved(false), 2000);
  };

  // Currently selected node object
  const selectedNode = useMemo(() => {
    return nodes.find((n) => n.id === selectedNodeId);
  }, [nodes, selectedNodeId]);

  return (
    <div className="relative w-full h-[72vh] rounded-lg overflow-hidden border border-border bg-surface shadow-inner">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        nodeTypes={nodeTypes}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        onNodeClick={(_, node) => setSelectedNodeId(node.id)}
        onPaneClick={() => setSelectedNodeId(null)}
        fitView
        fitViewOptions={{ padding: 0.2 }}
        proOptions={{ hideAttribution: true }}
      >
        <Background gap={24} color={themeMode === "dark" ? "#334155" : "#E2E8F0"} />
        <Controls />
        <MiniMap
          nodeColor={(node) => (node.data as CustomNodeData)?.bgColor || "#3B82F6"}
          maskColor={themeMode === "dark" ? "rgba(0, 0, 0, 0.6)" : "rgba(240, 240, 240, 0.6)"}
          pannable
          zoomable
        />

        {/* Top Control Panel */}
        <Panel position="top-left" className="flex items-center gap-2 bg-surface/90 backdrop-blur-md p-2 rounded-lg border border-border shadow-md">
          <Button size="sm" variant="primary" onClick={handleAddNode} title="Add a new custom node">
            <Plus size={14} /> Add Node
          </Button>
          <Button size="sm" variant="secondary" onClick={handleSaveLayout} title="Save layout to local storage">
            <Save size={14} /> {isSaved ? "Saved!" : "Save Layout"}
          </Button>
          <Button size="sm" variant="outline" onClick={handleResetLayout} title="Reset to auto-calculated layout">
            <RotateCcw size={14} /> Reset Layout
          </Button>
        </Panel>

        {/* Quick Instructions Badge */}
        <Panel position="top-right" className="bg-surface/80 backdrop-blur-md px-3 py-1.5 rounded-lg border border-border text-xs text-fg-soft shadow-sm hidden sm:flex items-center gap-2">
          <Sparkles size={13} className="text-amber-500" />
          <span>Double-click node to edit text &bull; Hover for color picker &bull; Drag handles to connect</span>
        </Panel>

        {/* Selected Node Properties Slide-Over Panel */}
        {selectedNode && (
          <Panel position="bottom-right" className="bg-surface/95 backdrop-blur-md p-3.5 rounded-xl border border-border shadow-xl w-72 space-y-3 z-30">
            <div className="flex items-center justify-between border-b border-border pb-2">
              <span className="text-xs font-bold uppercase tracking-wider text-fg-soft flex items-center gap-1.5">
                <Type size={13} /> Node Properties
              </span>
              <button
                onClick={() => setSelectedNodeId(null)}
                className="text-xs text-fg-soft hover:text-fg font-semibold"
              >
                &times;
              </button>
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-medium text-fg">Label Text</label>
              <input
                type="text"
                value={selectedNode.data.label || ""}
                onChange={(e) => handleLabelChange(selectedNode.id, e.target.value)}
                className="w-full text-xs px-2.5 py-1.5 rounded-md border border-border bg-surface-alt text-fg focus:outline-none focus:ring-1 focus:ring-primary"
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-medium text-fg flex items-center gap-1">
                <Palette size={12} /> Color Presets
              </label>
              <div className="grid grid-cols-4 gap-1.5">
                {PRESET_COLORS.map((preset, idx) => (
                  <button
                    key={idx}
                    onClick={() => handleColorChange(selectedNode.id, preset.bg, preset.border, preset.text)}
                    className="h-6 w-full rounded border transition-transform hover:scale-105 focus:outline-none"
                    style={{ backgroundColor: preset.bg, borderColor: preset.border }}
                    title={preset.name}
                  />
                ))}
              </div>
            </div>

            {!selectedNode.data.isHub && (
              <div className="pt-2 border-t border-border flex justify-end">
                <Button
                  size="sm"
                  variant="danger"
                  className="w-full"
                  onClick={() => handleDeleteNode(selectedNode.id)}
                >
                  Delete Node
                </Button>
              </div>
            )}
          </Panel>
        )}
      </ReactFlow>
    </div>
  );
}
