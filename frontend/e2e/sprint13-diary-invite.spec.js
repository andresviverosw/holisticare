/* global require */
/**
 * Sprint 13 — US-DIARY-AUTH-PROD smoke (mocked APIs).
 * Clinician creates invite → patient redeems via ?invite= → /diario.
 */
const { test, expect } = require("@playwright/test");

const PATIENT = "550e8400-e29b-41d4-a716-446655440000";
const INVITE_TOKEN = "test-invite-token-sprint13";

const CLINICIAN_JWT =
  "header.eyJzdWIiOiJkZXYtY2xpbmljaWFuIiwicm9sZSI6ImNsaW5pY2lhbiJ9.signature";
const PATIENT_JWT =
  "header.eyJzdWIiOiI1NTBlODQwMC1lMjliLTQxZDQtYTcxNi00NDY2NTU0NDAwMDAiLCJyb2xlIjoicGF0aWVudCJ9.signature";

async function mockClinicianLogin(page) {
  await page.route("**/api/auth/dev-login", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        access_token: CLINICIAN_JWT,
        token_type: "bearer",
        role: "clinician",
        sub: "dev-clinician",
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
}

test("Sprint 13: clinician creates invite link for patient", async ({ page }) => {
  await mockClinicianLogin(page);

  await page.route("**/api/rag/diary/invites", async (route) => {
    if (route.request().method() === "POST") {
      const body = route.request().postDataJSON();
      expect(body.patient_id).toBe(PATIENT);
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          invite_id: "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
          patient_id: PATIENT,
          expires_at: "2026-07-23T12:00:00Z",
          redeem_path: `/login?invite=${INVITE_TOKEN}`,
          redeem_url: `http://localhost:5173/login?invite=${INVITE_TOKEN}`,
          token: INVITE_TOKEN,
        }),
      });
      return;
    }
    await route.fallback();
  });

  await page.goto("/login");
  await page.getByRole("button", { name: "Entrar (desarrollo — clínico)" }).click();
  await expect(page).toHaveURL(/\/dashboard$/);

  await page.getByPlaceholder("Genera un ID nuevo o pega un UUID existente").fill(PATIENT);
  await page.getByRole("button", { name: "Invitar al diario" }).click();
  await expect(page.getByText("Enlace de invitación (un solo uso)")).toBeVisible();
  await expect(page.getByText(new RegExp(`invite=${INVITE_TOKEN}`))).toBeVisible();
});

test("Sprint 13: patient redeems invite query and opens /diario", async ({ page }) => {
  await page.route("**/api/auth/redeem-invite", async (route) => {
    const body = route.request().postDataJSON();
    expect(body.token).toBe(INVITE_TOKEN);
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        access_token: PATIENT_JWT,
        token_type: "bearer",
        role: "patient",
        sub: PATIENT,
        expires_at: "2026-08-15T12:00:00Z",
      }),
    });
  });

  await page.route(`**/api/rag/diary/patient/${PATIENT}**`, async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({ items: [] }),
    });
  });

  await page.goto(`/login?invite=${INVITE_TOKEN}`);
  await expect(page).toHaveURL(/\/diario$/);
  await expect(page.getByRole("heading", { name: "Mi diario" })).toBeVisible();
  await expect(page.getByRole("code")).toHaveText(PATIENT);
});
