import type { HTMLAttributes } from "react";
import { cn } from "@/lib/cn";
import type { ProjectStatus } from "@/lib/api/types";

export function Badge({
  className,
  ...props
}: HTMLAttributes<HTMLSpanElement>) {
  return <span className={cn("cg-badge", className)} {...props} />;
}

const statusStyles: Record<ProjectStatus, string> = {
  idea: "bg-warning/15 text-warning border-warning/30",
  active: "bg-success/15 text-success border-success/30",
  paused: "bg-muted/15 text-muted border-muted/30",
  archived: "bg-surface-alt text-fg-soft border-border",
};

export function StatusBadge({ status }: { status: ProjectStatus }) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full border px-2 py-0.5 text-xs font-medium capitalize",
        statusStyles[status]
      )}
    >
      {status}
    </span>
  );
}
