import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api/endpoints";
import { qk } from "@/lib/api/keys";
import { Card, CardContent } from "@/components/ui/Card";
import { LoadingState, ErrorState, EmptyState } from "@/components/ui/Empty";

export default function Tags() {
  const { data, isLoading, error } = useQuery({
    queryKey: qk.tags,
    queryFn: api.listTags,
  });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Tags</h1>
        <p className="mt-1 text-fg-soft">
          Browse and filter projects by tag.
        </p>
      </div>

      {isLoading && <LoadingState />}
      {error && <ErrorState error={error} />}
      {data && data.tags.length === 0 && (
        <EmptyState
          title="No tags yet"
          description="Add tags to projects from their detail page."
        />
      )}

      <Card>
        <CardContent className="flex flex-wrap gap-2">
          {data?.tags.map((t) => (
            <Link
              key={t.name}
              to={`/projects?tag=${encodeURIComponent(t.name)}`}
              className="cg-badge text-sm hover:bg-primary/10 hover:text-primary hover:border-primary/30"
            >
              {t.name}
              <span className="ml-2 text-xs text-fg-soft">{t.project_count}</span>
            </Link>
          ))}
        </CardContent>
      </Card>
    </div>
  );
}
