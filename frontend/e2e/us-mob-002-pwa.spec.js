/* global require */
const { test, expect } = require("@playwright/test");

const IPHONE_VIEWPORT = { width: 390, height: 844 };

test.describe("US-MOB-002 installable PWA shell", () => {
  test.use({ viewport: IPHONE_VIEWPORT });

  test("serves installable web manifest with HolistiCare branding", async ({ page }) => {
    await page.goto("/login");
    const manifestHref = await page.locator('link[rel="manifest"]').getAttribute("href");
    expect(manifestHref).toBeTruthy();

    const manifestUrl = new URL(manifestHref, page.url()).toString();
    const res = await page.request.get(manifestUrl);
    expect(res.ok()).toBeTruthy();
    const manifest = await res.json();
    expect(manifest.name).toBe("HolistiCare");
    expect(manifest.short_name).toBe("HolistiCare");
    expect(manifest.display).toBe("standalone");
    expect(manifest.icons.some((i) => String(i.sizes).includes("192x192"))).toBeTruthy();
    expect(manifest.icons.some((i) => String(i.sizes).includes("512x512"))).toBeTruthy();
  });

  test("registers a service worker and shows deterministic offline messaging", async ({ page }) => {
    await page.goto("/login");

    await expect
      .poll(async () => page.evaluate(async () => {
        const regs = await navigator.serviceWorker.getRegistrations();
        return regs.length;
      }), { timeout: 15000 })
      .toBeGreaterThan(0);

    await page.evaluate(() => {
      Object.defineProperty(navigator, "onLine", { configurable: true, get: () => false });
      window.dispatchEvent(new Event("offline"));
    });
    await expect(page.getByTestId("offline-banner")).toBeVisible();
    await expect(page.getByTestId("offline-banner")).toContainText(/sin conexi[oó]n|no disponible/i);

    const offline = await page.request.get("/offline.html");
    expect(offline.ok()).toBeTruthy();
    const html = await offline.text();
    expect(html).toMatch(/Sin conexión|no disponible/i);
    expect(html).toMatch(/HolistiCare/);
  });

  test("keeps JWT session token across reload (home-screen reopen continuity)", async ({ page }) => {
    await page.goto("/login");
    await page.evaluate(() => {
      localStorage.setItem("holisticare_token", "pwa-session-token");
    });
    await page.reload();
    const token = await page.evaluate(() => localStorage.getItem("holisticare_token"));
    expect(token).toBe("pwa-session-token");
  });
});
