import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";
import { VitePWA } from "vite-plugin-pwa";
import { buildWebManifest } from "./src/utils/pwaConfig.js";

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "");
  const target = env.VITE_PROXY_TARGET || "http://127.0.0.1:8000";
  const enablePwaInDev = env.VITE_PWA_DEV === "true";

  return {
    plugins: [
      react(),
      VitePWA({
        registerType: "autoUpdate",
        includeAssets: ["offline.html", "icons/icon-192.png", "icons/icon-512.png"],
        manifest: buildWebManifest(),
        workbox: {
          navigateFallback: "index.html",
          navigateFallbackDenylist: [/^\/api/],
          runtimeCaching: [
            {
              urlPattern: ({ url }) => url.pathname.startsWith("/api"),
              handler: "NetworkOnly",
            },
          ],
        },
        devOptions: {
          // Playwright e2e uses `npm run dev`; enable SW there for US-MOB-002 checks.
          enabled: enablePwaInDev,
          navigateFallback: "index.html",
        },
      }),
    ],
    test: {
      environment: "node",
      include: ["src/**/*.test.js"],
    },
    server: {
      host: "0.0.0.0",
      port: 5173,
      proxy: {
        "/api": {
          target,
          changeOrigin: true,
          rewrite: (path) => path.replace(/^\/api/, ""),
        },
      },
    },
  };
});
