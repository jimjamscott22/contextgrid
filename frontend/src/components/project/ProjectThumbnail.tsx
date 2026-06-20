import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api/endpoints";
import { qk } from "@/lib/api/keys";
import { cn } from "@/lib/cn";
import type { Project } from "@/lib/api/types";

/**
 * Refined-minimal cover image for a project card.
 *
 * The cover is the project's first screenshot (uploaded via the Screenshots
 * panel). Projects without a screenshot get a generated placeholder — a faint
 * grid texture with the project's monogram and a subtle, deterministic accent
 * tint — so every card reads as intentional rather than empty.
 */
export function ProjectThumbnail({
  project,
  className,
}: {
  project: Project;
  className?: string;
}) {
  const [loaded, setLoaded] = useState(false);
  const [failed, setFailed] = useState(false);

  const { data } = useQuery({
    queryKey: qk.screenshots(project.id),
    queryFn: () => api.listScreenshots(project.id),
    staleTime: 5 * 60 * 1000,
  });

  const cover = data?.screenshots[0];
  const hasImage = !!cover && !failed;
  const { hue, monogram } = derive(project.name);

  return (
    <div
      className={cn(
        "relative aspect-[16/9] w-full overflow-hidden border-b border-border bg-surface-alt",
        className,
      )}
    >
      {/* Placeholder — always rendered underneath so it shows during load,
          on error, and for projects with no screenshot. */}
      <Placeholder hue={hue} monogram={monogram} />

      {hasImage && (
        <img
          src={cover.url}
          alt={cover.label || `${project.name} cover`}
          loading="lazy"
          onLoad={() => setLoaded(true)}
          onError={() => setFailed(true)}
          className={cn(
            "absolute inset-0 h-full w-full object-cover",
            "transition-[opacity,transform] duration-500 ease-out",
            "group-hover:scale-[1.03]",
            loaded ? "opacity-100" : "opacity-0",
          )}
        />
      )}

      {/* Top sheen for legibility of anything overlaid, kept barely-there. */}
      <div className="pointer-events-none absolute inset-x-0 top-0 h-px bg-white/10" />
    </div>
  );
}

function Placeholder({ hue, monogram }: { hue: number; monogram: string }) {
  return (
    <div
      className="absolute inset-0 grid place-items-center"
      style={{
        // Deterministic, low-opacity accent so cards are distinguishable
        // without fighting the active theme.
        backgroundImage: `radial-gradient(120% 120% at 100% 0%, hsl(${hue} 70% 55% / 0.14), transparent 60%)`,
      }}
      aria-hidden
    >
      {/* The "grid" in ContextGrid: hairline lattice, very faint. */}
      <div
        className="absolute inset-0 opacity-[0.5]"
        style={{
          backgroundImage:
            "linear-gradient(rgb(var(--cg-border) / 0.6) 1px, transparent 1px), linear-gradient(90deg, rgb(var(--cg-border) / 0.6) 1px, transparent 1px)",
          backgroundSize: "22px 22px",
          maskImage:
            "radial-gradient(120% 120% at 50% 40%, black, transparent 75%)",
          WebkitMaskImage:
            "radial-gradient(120% 120% at 50% 40%, black, transparent 75%)",
        }}
      />
      <span
        className="relative select-none font-semibold tracking-tight text-fg-soft"
        style={{ fontSize: "clamp(1.75rem, 6vw, 2.75rem)" }}
      >
        {monogram}
      </span>
      <span
        className="absolute bottom-3 right-3 h-1.5 w-1.5 rounded-full"
        style={{ background: `hsl(${hue} 70% 55% / 0.7)` }}
      />
    </div>
  );
}

/** Stable hue + monogram derived from the project name. */
function derive(name: string): { hue: number; monogram: string } {
  const trimmed = name.trim();
  let hash = 0;
  for (let i = 0; i < trimmed.length; i++) {
    hash = (hash * 31 + trimmed.charCodeAt(i)) >>> 0;
  }
  const hue = hash % 360;

  const words = trimmed.split(/[\s_\-/]+/).filter(Boolean);
  const monogram =
    words.length >= 2
      ? (words[0][0] + words[1][0]).toUpperCase()
      : trimmed.slice(0, 2).toUpperCase() || "·";

  return { hue, monogram };
}
