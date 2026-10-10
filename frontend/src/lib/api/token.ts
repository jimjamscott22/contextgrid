/** Shared API bearer token for dev/prod builds (optional). */
export function getApiToken(): string | undefined {
  const value = import.meta.env.VITE_API_TOKEN;
  if (typeof value !== "string") return undefined;
  const trimmed = value.trim();
  return trimmed.length > 0 ? trimmed : undefined;
}
