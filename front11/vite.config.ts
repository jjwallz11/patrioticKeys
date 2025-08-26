// vite.config.ts
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig(({ mode }) => ({
  plugins: [react()],
  assetsInclude: ["**/*.PNG"],
  // Only proxy in development; in production we hit the real API URL.
  server: mode === "development"
    ? {
        open: true,
        proxy: {
          "/api": "http://127.0.0.1:2913",
        },
      }
    : undefined,
}));