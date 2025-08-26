// vite.config.ts
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig(({ mode }) => ({
  plugins: [react()],
  assetsInclude: ["**/*.PNG"],
  envPrefix: "VITE_",
}));