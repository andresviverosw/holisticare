/** US-MOB-002 — register generated service worker (no-op when PWA plugin is absent). */

export async function registerHolistiCarePwa() {
  if (typeof window === "undefined") return { registered: false };
  if (!("serviceWorker" in navigator)) return { registered: false };

  try {
    const { registerSW } = await import("virtual:pwa-register");
    registerSW({ immediate: true });
    return { registered: true };
  } catch {
    return { registered: false };
  }
}
