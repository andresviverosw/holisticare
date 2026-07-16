/* global require */
/**
 * Sprint 14 — US-AUTH-CLINICIAN-PROD smoke (mocked APIs).
 * Password login → /dashboard.
 */
const { test, expect } = require("@playwright/test");

const CLINICIAN_JWT =
  "header.eyJzdWIiOiIxMTExMTExMS0xMTExLTQxMTEtODExMS0xMTExMTExMTExMTEiLCJyb2xlIjoiY2xpbmljaWFuIn0.signature";

test("Sprint 14: clinician password login opens dashboard", async ({ page }) => {
  await page.route("**/api/auth/login", async (route) => {
    const body = route.request().postDataJSON();
    expect(body.username).toBe("clinician1");
    expect(body.password).toBe("s3cret");
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        access_token: CLINICIAN_JWT,
        token_type: "bearer",
        role: "clinician",
        sub: "11111111-1111-4111-8111-111111111111",
        expires_at: "2026-07-16T12:00:00Z",
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
  await page.getByLabel("Usuario").fill("clinician1");
  await page.getByLabel("Contraseña").fill("s3cret");
  await page.getByRole("button", { name: "Entrar", exact: true }).click();
  await expect(page).toHaveURL(/\/dashboard$/);
  await expect(page.getByRole("heading", { name: /Generador de planes/i })).toBeVisible();
});

test("Sprint 14: wrong password shows error and stays on login", async ({ page }) => {
  await page.route("**/api/auth/login", async (route) => {
    await route.fulfill({
      status: 401,
      contentType: "application/json",
      body: JSON.stringify({ detail: "Invalid username or password" }),
    });
  });

  await page.goto("/login");
  await page.getByLabel("Usuario").fill("clinician1");
  await page.getByLabel("Contraseña").fill("wrong");
  await page.getByRole("button", { name: "Entrar", exact: true }).click();
  await expect(page).toHaveURL(/\/login/);
  await expect(page.getByRole("alert")).toBeVisible();
});
