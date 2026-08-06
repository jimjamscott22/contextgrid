import { useState, useRef, useEffect, memo } from "react";
import { Handle, Position, type NodeProps } from "reactflow";
import { Edit2, Palette, Trash2, Check, X } from "lucide-react";

export interface CustomNodeData {
  label: string;
  status?: "idea" | "active" | "paused" | "archived" | string;
  bgColor?: string;
  borderColor?: string;
  textColor?: string;
  isHub?: boolean;
  nodeType?: "hub" | "project" | "status" | "tag" | "custom";
  onLabelChange?: (id: string, newLabel: string) => void;
  onColorChange?: (id: string, bgColor: string, borderColor: string, textColor: string) => void;
  onDeleteNode?: (id: string) => void;
}

export const PRESET_COLORS = [
  { name: "Yellow (Idea)", bg: "#FEF08A", border: "#EAB308", text: "#854D0E" },
  { name: "Green (Active)", bg: "#DCFCE7", border: "#22C55E", text: "#166534" },
  { name: "Purple (Paused)", bg: "#F3E8FF", border: "#A855F7", text: "#6B21A8" },
  { name: "Blue (Primary)", bg: "#DBEAFE", border: "#3B82F6", text: "#1E40AF" },
  { name: "Rose (Notice)", bg: "#FFE4E6", border: "#F43F5E", text: "#9F1239" },
  { name: "Slate (Archived)", bg: "#F1F5F9", border: "#64748B", text: "#334155" },
  { name: "Dark Indigo", bg: "#1E1B4B", border: "#6366F1", text: "#EEF2FF" },
  { name: "Dark Emerald", bg: "#064E3B", border: "#10B981", text: "#ECFDF5" },
];

function EditableNodeComponent({ id, data, selected }: NodeProps<CustomNodeData>) {
  const [isEditing, setIsEditing] = useState(false);
  const [label, setLabel] = useState(data.label || "");
  const [showColorPicker, setShowColorPicker] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    setLabel(data.label || "");
  }, [data.label]);

  useEffect(() => {
    if (isEditing) {
      inputRef.current?.focus();
      inputRef.current?.select();
    }
  }, [isEditing]);

  const handleSaveLabel = () => {
    setIsEditing(false);
    const trimmed = label.trim();
    if (trimmed && trimmed !== data.label) {
      data.onLabelChange?.(id, trimmed);
    } else {
      setLabel(data.label);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") {
      handleSaveLabel();
    } else if (e.key === "Escape") {
      setIsEditing(false);
      setLabel(data.label);
    }
  };

  const currentBg = data.bgColor || (data.isHub ? "#1D4ED8" : "#FEF08A");
  const currentBorder = data.borderColor || (data.isHub ? "#3B82F6" : "#EAB308");
  const currentText = data.textColor || (data.isHub ? "#FFFFFF" : "#1E293B");

  return (
    <div
      className={`group relative rounded-lg shadow-sm transition-all duration-150 ${
        selected ? "ring-2 ring-primary ring-offset-2 ring-offset-background" : ""
      }`}
      style={{
        backgroundColor: currentBg,
        borderColor: currentBorder,
        borderWidth: "2px",
        borderStyle: "solid",
        color: currentText,
        minWidth: data.isHub ? "140px" : "120px",
        padding: data.isHub ? "12px 18px" : "8px 14px",
      }}
    >
      {/* Handles on 4 sides for flexible connecting */}
      <Handle type="target" position={Position.Top} id="top" className="!bg-primary/70 !w-2.5 !h-2.5" />
      <Handle type="source" position={Position.Bottom} id="bottom" className="!bg-primary/70 !w-2.5 !h-2.5" />
      <Handle type="target" position={Position.Left} id="left" className="!bg-primary/70 !w-2.5 !h-2.5" />
      <Handle type="source" position={Position.Right} id="right" className="!bg-primary/70 !w-2.5 !h-2.5" />

      {/* Main content */}
      <div className="flex flex-col items-center justify-center gap-1 text-center">
        {data.status && !data.isHub && (
          <span
            className="text-[10px] font-semibold tracking-wider uppercase opacity-85 px-1.5 py-0.5 rounded"
            style={{ backgroundColor: "rgba(0, 0, 0, 0.08)" }}
          >
            {data.status}
          </span>
        )}

        {isEditing ? (
          <div className="flex items-center gap-1 w-full" onClick={(e) => e.stopPropagation()}>
            <input
              ref={inputRef}
              type="text"
              value={label}
              onChange={(e) => setLabel(e.target.value)}
              onKeyDown={handleKeyDown}
              onBlur={handleSaveLabel}
              className="w-full text-xs font-semibold px-1 py-0.5 rounded border border-primary text-fg bg-surface shadow-inner focus:outline-none"
            />
            <button
              onClick={handleSaveLabel}
              className="p-1 text-emerald-600 hover:bg-emerald-50 rounded"
              title="Save"
            >
              <Check size={12} />
            </button>
            <button
              onClick={() => {
                setIsEditing(false);
                setLabel(data.label);
              }}
              className="p-1 text-rose-600 hover:bg-rose-50 rounded"
              title="Cancel"
            >
              <X size={12} />
            </button>
          </div>
        ) : (
          <div
            onDoubleClick={(e) => {
              e.stopPropagation();
              setIsEditing(true);
            }}
            className="cursor-pointer text-xs font-bold leading-tight select-none px-1 py-0.5 rounded hover:bg-black/5"
            title="Double-click to edit text"
          >
            {data.label}
          </div>
        )}
      </div>

      {/* Quick Action Overlay (Hover / Selected) */}
      <div
        className={`absolute -top-9 left-1/2 -translate-x-1/2 flex items-center gap-1 p-1 bg-surface border border-border rounded-md shadow-md transition-opacity duration-150 z-20 ${
          selected ? "opacity-100 pointer-events-auto" : "opacity-0 group-hover:opacity-100 pointer-events-auto"
        }`}
        onClick={(e) => e.stopPropagation()}
      >
        <button
          onClick={() => setIsEditing(true)}
          className="p-1 text-fg-soft hover:text-fg hover:bg-surface-alt rounded transition-colors"
          title="Edit text label"
        >
          <Edit2 size={13} />
        </button>
        <button
          onClick={() => setShowColorPicker(!showColorPicker)}
          className="p-1 text-fg-soft hover:text-fg hover:bg-surface-alt rounded transition-colors"
          title="Change color theme"
        >
          <Palette size={13} />
        </button>
        {data.onDeleteNode && !data.isHub && (
          <button
            onClick={() => data.onDeleteNode?.(id)}
            className="p-1 text-danger hover:bg-danger/10 rounded transition-colors"
            title="Delete node"
          >
            <Trash2 size={13} />
          </button>
        )}
      </div>

      {/* Color Palette Popover */}
      {showColorPicker && (
        <div
          className="absolute left-1/2 top-full mt-2 -translate-x-1/2 p-2 bg-surface border border-border rounded-lg shadow-xl z-30 grid grid-cols-4 gap-1.5 w-44"
          onClick={(e) => e.stopPropagation()}
        >
          {PRESET_COLORS.map((preset, idx) => (
            <button
              key={idx}
              onClick={() => {
                data.onColorChange?.(id, preset.bg, preset.border, preset.text);
                setShowColorPicker(false);
              }}
              title={preset.name}
              className="h-6 w-full rounded border transition-transform hover:scale-110 focus:outline-none"
              style={{
                backgroundColor: preset.bg,
                borderColor: preset.border,
              }}
            />
          ))}
          <div className="col-span-4 border-t border-border pt-1 mt-1 flex justify-between items-center text-[10px]">
            <span className="text-fg-soft">Custom:</span>
            <input
              type="color"
              value={currentBg}
              onChange={(e) => {
                const hex = e.target.value;
                // auto-calculate dark vs light text
                const textHex = parseInt(hex.replace("#", ""), 16) > 0x888888 ? "#1E293B" : "#FFFFFF";
                data.onColorChange?.(id, hex, hex, textHex);
              }}
              className="w-5 h-5 cursor-pointer rounded border border-border p-0 bg-transparent"
            />
          </div>
        </div>
      )}
    </div>
  );
}

export const EditableNode = memo(EditableNodeComponent);
