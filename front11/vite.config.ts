import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";
import { fileURLToPath } from "url";
import { dirname, resolve } from "path";
import legacy from "@vitejs/plugin-legacy";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, resolve(__dirname, ".."), "");

  return {
    base: "/static/",
    plugins: [
      react(),
      legacy({
        targets: ["defaults", "not IE 11"],
      }),
    ],
    define: {
      "import.meta.env.VITE_API_BASE_URL": JSON.stringify(
        env.VITE_API_BASE_URL
      ),
    },
    server: {
      open: true,
    },
    build: {
      target: "es2015",
    },
  };
});
