import { useState } from "react";
import { languageBadgeUrl, projectLanguage } from "@/lib/projectLanguages";

/** Render a compact Shields.io language badge with a readable offline fallback. */
export function LanguageBadge({ language }: { language?: string | null }) {
  const resolved = projectLanguage(language);
  const src = resolved ? languageBadgeUrl(resolved) : null;
  const [failedSrc, setFailedSrc] = useState<string | null>(null);
  if (!src || src === failedSrc) {
    return (
      <span className="max-w-24 truncate rounded bg-surface-alt px-1.5 py-0.5 text-[10px] text-fg-soft" title={resolved?.name}>
        {resolved?.name ?? "Unspecified"}
      </span>
    );
  }
  return (
    <img
      src={src}
      alt={resolved!.name}
      title={resolved!.name}
      referrerPolicy="no-referrer"
      loading="lazy"
      className="h-5 max-w-24 shrink-0 object-contain"
      onError={() => setFailedSrc(src)}
    />
  );
}
