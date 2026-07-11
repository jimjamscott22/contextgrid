import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";
import path from "node:path";
import { visualizer } from "rollup-plugin-visualizer";
/// <reference types="vitest" />

export default defineConfig({
  plugins: [
    react(),
    process.env.ANALYZE === "1" &&
      visualizer({
        filename: "dist/stats.html",
        gzipSize: true,
        brotliSize: true,
        open: false,
      }),
  ].filter(Boolean),
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  server: {
    port: 5173,
    host: "0.0.0.0",
    proxy: {
      "/api": {
        target: process.env.API_ENDPOINT || "http://localhost:8003",
        changeOrigin: true,
      },
      // Uploaded screenshots/covers are served by the API as static files.
      // Without this, /uploads/* requests hit the Vite dev server and return
      // index.html, so project thumbnails and the Screenshots panel render broken.
      "/uploads": {
        target: process.env.API_ENDPOINT || "http://localhost:8003",
        changeOrigin: true,
      },
    },
  },
  build: {
    outDir: "dist",
    sourcemap: true,
  },
  test: {
    environment: "jsdom",
    globals: true,
  },
});
