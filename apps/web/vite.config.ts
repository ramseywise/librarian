import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

const apiTarget = process.env.VITE_API_URL ?? "http://localhost:8000";

export default defineConfig({
  plugins: [react()],
  build: {
    rolldownOptions: {
      output: {
        // Keep the graph stack and the markdown stack out of the app chunk so each
        // caches independently (KaTeX already loads lazily with the course views).
        codeSplitting: {
          groups: [
            { name: "graph-vendor", test: /node_modules[\\/](@xyflow|d3-|dagre|@dagrejs)/ },
            { name: "markdown-vendor", test: /node_modules[\\/](react-markdown|remark-|micromark|mdast-|hast-|unified|unist-|vfile)/ },
          ],
        },
      },
    },
  },
  server: {
    port: 5173,
    proxy: {
      "/api": {
        target: apiTarget,
        changeOrigin: true,
      },
      // Graph live updates; the client connects to ws(s)://<page host>/ws.
      "/ws": {
        target: apiTarget,
        ws: true,
        changeOrigin: true,
      },
    },
  },
});
