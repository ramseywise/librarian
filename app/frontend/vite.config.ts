import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

const apiTarget = process.env.VITE_API_URL ?? "http://localhost:8000";

export default defineConfig({
  plugins: [react()],
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
