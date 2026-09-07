import { describe, expect, it } from "vitest";
import {
  OFFLINE_UNAVAILABLE_MESSAGE,
  PWA_DISPLAY_MODE,
  PWA_SHORT_NAME,
  buildWebManifest,
  isInstallableManifest,
  shouldShowOfflineBanner,
} from "./pwaConfig";

describe("US-MOB-002 pwaConfig", () => {
  it("buildWebManifest exposes HolistiCare branding and standalone display", () => {
    const manifest = buildWebManifest();
    expect(manifest.name).toBe("HolistiCare");
    expect(manifest.short_name).toBe(PWA_SHORT_NAME);
    expect(manifest.display).toBe(PWA_DISPLAY_MODE);
    expect(manifest.lang).toBe("es");
    expect(manifest.start_url).toBe("/");
    expect(manifest.theme_color).toMatch(/^#[0-9a-fA-F]{6}$/);
    expect(manifest.icons.length).toBeGreaterThanOrEqual(2);
    expect(manifest.icons.every((icon) => icon.src && icon.sizes && icon.type)).toBe(true);
  });

  it("isInstallableManifest requires name, standalone display, and 192+512 icons", () => {
    expect(isInstallableManifest(buildWebManifest())).toBe(true);
    expect(
      isInstallableManifest({
        ...buildWebManifest(),
        display: "browser",
      }),
    ).toBe(false);
    expect(
      isInstallableManifest({
        ...buildWebManifest(),
        icons: [{ src: "/icons/icon-192.png", sizes: "192x192", type: "image/png" }],
      }),
    ).toBe(false);
  });

  it("offline messaging is deterministic Spanish copy (no blank shell)", () => {
    expect(OFFLINE_UNAVAILABLE_MESSAGE).toMatch(/sin conexi[oó]n|no disponible/i);
    expect(OFFLINE_UNAVAILABLE_MESSAGE.length).toBeGreaterThan(20);
  });

  it("shouldShowOfflineBanner is true only when explicitly offline", () => {
    expect(shouldShowOfflineBanner({ onLine: false })).toBe(true);
    expect(shouldShowOfflineBanner({ onLine: true })).toBe(false);
    expect(shouldShowOfflineBanner({})).toBe(false);
  });
});
