import { useEffect, useRef, useState } from "react";
import mermaid from "mermaid";
import { useTheme } from "@/components/ThemeProvider";

let initialized = false;

interface MermaidProps {
  chart: string;
  id?: string;
}

export function Mermaid({ chart, id }: MermaidProps) {
  const ref = useRef<HTMLDivElement>(null);
  const { themeMode } = useTheme();
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!initialized) {
      mermaid.initialize({
        startOnLoad: false,
        securityLevel: "strict",
        theme: themeMode === "dark" ? "dark" : "default",
      });
      initialized = true;
    } else {
      mermaid.initialize({
        startOnLoad: false,
        securityLevel: "strict",
        theme: themeMode === "dark" ? "dark" : "default",
      });
    }
  }, [themeMode]);

  useEffect(() => {
    let cancelled = false;
    if (!ref.current) return;
    const renderId = id || `mermaid-${Math.random().toString(36).slice(2)}`;
    mermaid
      .render(renderId, chart)
      .then(({ svg }) => {
        if (!cancelled && ref.current) {
          ref.current.innerHTML = svg;
        }
        if (!cancelled) setError(null);
      })
      .catch((err) => {
        if (!cancelled) {
          setError(String(err));
        }
      });
    return () => {
      cancelled = true;
    };
  }, [chart, id, themeMode]);

  return (
    <>
      <div ref={ref} className="overflow-x-auto" />
      {error && <pre className="text-danger text-xs">{error}</pre>}
    </>
  );
}
