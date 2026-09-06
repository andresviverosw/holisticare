/* global require */
const { test, expect } = require("@playwright/test");

const IPHONE_VIEWPORT = { width: 390, height: 844 };

test.describe("US-MOB-001 clinician mobile shell", () => {
  test("drawer menu reveals nav and dashboard content is not crushed", async ({ page }) => {
    await page.setViewportSize(IPHONE_VIEWPORT);

    await page.route("**/api/health", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ status: "ok" }),
      });
    });

    await page.route("**/api/auth/dev-login", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          access_token: "header.eyJzdWIiOiJkZXYtY2xpbmljaWFuIiwicm9sZSI6ImNsaW5pY2lhbiJ9.signature",
          token_type: "bearer",
        }),
      });
    });

    await page.route("**/api/rag/plan/memory-bank**", async (route) => {
      if (route.request().method() === "GET") {
        await route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({ items: [] }),
        });
        return;
      }
      await route.fallback();
    });

    await page.goto("/login");
    await page.getByRole("button", { name: "Entrar (desarrollo — clínico)" }).click();
    await expect(page).toHaveURL(/\/dashboard$/);

    const heading = page.getByRole("heading", {
      name: /Generador de planes de tratamiento/i,
    });
    await expect(heading).toBeVisible();

    const box = await heading.boundingBox();
    expect(box).toBeTruthy();
    expect(box.width).toBeGreaterThan(200);

    await page.getByRole("button", { name: "Menú" }).click();
    await expect(page.getByRole("dialog", { name: "Navegación" })).toBeVisible();
    await expect(page.getByRole("link", { name: /Dashboard/i })).toBeVisible();
    await expect(page.getByRole("link", { name: /Base de conocimiento/i })).toBeVisible();
  });
});

test.describe("US-UX-COLDSTART-001 login hint", () => {
  test("shows cold-start status after a slow auth response", async ({ page }) => {
    await page.route("**/api/health", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ status: "ok" }),
      });
    });

    await page.route("**/api/auth/dev-login", async (route) => {
      await new Promise((r) => setTimeout(r, 3200));
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          access_token: "header.eyJzdWIiOiJkZXYtY2xpbmljaWFuIiwicm9sZSI6ImNsaW5pY2lhbiJ9.signature",
          token_type: "bearer",
        }),
      });
    });

    await page.goto("/login");
    await page.getByRole("button", { name: "Entrar (desarrollo — clínico)" }).click();
    await expect(page.getByRole("status")).toContainText(/API|Despertando|despert/i, {
      timeout: 5000,
    });
  });
});
