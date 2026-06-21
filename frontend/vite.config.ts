import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "node:path";

export default defineConfig({
  plugins: [react()],
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
});
