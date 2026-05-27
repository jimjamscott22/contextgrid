import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]): string {
  return twMerge(clsx(inputs));
}

export function formatDate(value?: string | null): string {
  if (!value) return "";
  const d = new Date(value);
  if (Number.isNaN(d.getTime())) return value;
  return d.toLocaleDateString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

export function formatDateTime(value?: string | null): string {
  if (!value) return "";
  const d = new Date(value);
  if (Number.isNaN(d.getTime())) return value;
  return d.toLocaleString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function statusColor(status?: string | null): string {
  switch (status) {
    case "active":
      return "bg-success/15 text-success border-success/30";
    case "idea":
      return "bg-warning/15 text-warning border-warning/30";
    case "paused":
      return "bg-fg-soft/15 text-fg-soft border-fg-soft/30";
    case "archived":
      return "bg-muted/20 text-muted border-muted/30";
    case "completed":
      return "bg-success/15 text-success border-success/30";
    default:
      return "bg-surface-alt text-fg-soft border-border";
  }
}
