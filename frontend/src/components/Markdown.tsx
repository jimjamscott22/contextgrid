import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import rehypeSanitize from "rehype-sanitize";
import { cn } from "@/lib/cn";

interface MarkdownProps {
  source: string | null | undefined;
  className?: string;
}

/**
 * Markdown renderer with GitHub-flavored markdown + HTML sanitization.
 * Styling is done via the `.cg-markdown` class scoped in index.css rather
 * than relying on @tailwindcss/typography to keep the dep list lean.
 */
export function Markdown({ source, className }: MarkdownProps) {
  if (!source) return null;
  return (
    <div className={cn("cg-markdown text-sm text-fg", className)}>
      <ReactMarkdown remarkPlugins={[remarkGfm]} rehypePlugins={[rehypeSanitize]}>
        {source}
      </ReactMarkdown>
    </div>
  );
}
