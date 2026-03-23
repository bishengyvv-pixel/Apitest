import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";
import path from "path";
import { defineConfig } from "vite";

export default defineConfig(({ command }) => ({
  plugins: [
    // The React and Tailwind plugins are both required for Make, even if
    // Tailwind is not being actively used. Do not remove them.
    react(),
    tailwindcss(),
  ],
  // Dev should run from "/", while the packaged app is served under "/assets/".
  base: command === "build" ? "/assets/" : "/",
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  server: {
    proxy: {
      "/api": "http://127.0.0.1:8765",
      "/assets/default-vision.png": "http://127.0.0.1:8765",
    },
  },
  build: {
    outDir: path.resolve(__dirname, "../packages/ai_api_tester_web/assets"),
    assetsDir: ".",
    emptyOutDir: false,
  },
  // File types to support raw imports. Never add .css, .tsx, or .ts files to this.
  assetsInclude: ["**/*.svg", "**/*.csv"],
}));
