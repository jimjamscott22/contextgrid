import type { ImgHTMLAttributes } from "react";

import { useAuthenticatedImageSrc } from "@/hooks/useAuthenticatedImageSrc";

type AuthenticatedImageProps = ImgHTMLAttributes<HTMLImageElement>;

/** Image that loads protected /uploads URLs when VITE_API_TOKEN is set. */
export function AuthenticatedImage({ src, ...props }: AuthenticatedImageProps) {
  const resolved = useAuthenticatedImageSrc(typeof src === "string" ? src : undefined);
  if (!resolved) return null;
  return <img src={resolved} {...props} />;
}
