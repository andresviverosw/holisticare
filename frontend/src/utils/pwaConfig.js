/** US-MOB-002 — installable PWA shell config (pure helpers). */

export const PWA_SHORT_NAME = "HolistiCare";
export const PWA_DISPLAY_MODE = "standalone";

export const OFFLINE_UNAVAILABLE_MESSAGE =
  "Sin conexión o servicio no disponible. Revisa tu red e intenta de nuevo. La sesión se mantiene si ya iniciaste sesión.";

const BRAND_THEME = "#2d9b5f";
const BRAND_BACKGROUND = "#f8f9fa";

export function buildWebManifest() {
  return {
    name: "HolistiCare",
    short_name: PWA_SHORT_NAME,
    description: "Apoyo clínico con IA para rehabilitación holística",
    lang: "es",
    start_url: "/",
    scope: "/",
    display: PWA_DISPLAY_MODE,
    background_color: BRAND_BACKGROUND,
    theme_color: BRAND_THEME,
    icons: [
      {
        src: "/icons/icon-192.png",
        sizes: "192x192",
        type: "image/png",
        purpose: "any",
      },
      {
        src: "/icons/icon-512.png",
        sizes: "512x512",
        type: "image/png",
        purpose: "any",
      },
      {
        src: "/icons/icon-512.png",
        sizes: "512x512",
        type: "image/png",
        purpose: "maskable",
      },
    ],
  };
}

function hasIconSize(icons, size) {
  return (icons || []).some((icon) => String(icon.sizes || "").split(" ").includes(size));
}

/** Chrome installability baseline: name, standalone/fullscreen/minimal-ui, 192 + 512 icons. */
export function isInstallableManifest(manifest) {
  if (!manifest || typeof manifest !== "object") return false;
  const name = String(manifest.name || manifest.short_name || "").trim();
  if (!name) return false;
  const display = String(manifest.display || "").toLowerCase();
  if (!["standalone", "fullscreen", "minimal-ui"].includes(display)) return false;
  const icons = manifest.icons || [];
  return hasIconSize(icons, "192x192") && hasIconSize(icons, "512x512");
}

export function shouldShowOfflineBanner(network = {}) {
  return network.onLine === false;
}
