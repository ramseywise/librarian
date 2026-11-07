import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";

// Separate from vite.config.ts so test setup and dev-server config change independently.
export default defineConfig({
  plugins: [react()],
  test: {
    environment: "jsdom",
    setupFiles: ["./src/test/setup.ts"],
    include: ["src/**/*.test.{ts,tsx}"],
    css: false,
    coverage: {
      provider: "v8",
      include: ["src/**/*.{ts,tsx}"],
      exclude: ["src/**/*.test.{ts,tsx}", "src/**/__tests__/**", "src/test/**", "src/**/*.d.ts", "src/main.tsx"],
      reporter: ["text-summary"],
      thresholds: { lines: 65, statements: 64, functions: 60, branches: 56 },
    },
  },
});
