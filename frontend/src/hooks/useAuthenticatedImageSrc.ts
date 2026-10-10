import { getApiToken } from "@/lib/api/token";

/**
 * Resolve an upload URL for use in <img src>. When VITE_API_TOKEN is set,
 * appends a token query parameter (uploads accept Bearer or ?token=).
 */
export function useAuthenticatedImageSrc(url: string | undefined): string | undefined {
  if (!url) return undefined;

  const token = getApiToken();
  if (!token || !url.startsWith("/uploads")) {
    return url;
  }

  const separator = url.includes("?") ? "&" : "?";
  return `${url}${separator}token=${encodeURIComponent(token)}`;
}
