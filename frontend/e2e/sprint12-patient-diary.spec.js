/* global require */
/**
 * Sprint 12 — US-DIARY-UI-PATIENT smoke (mocked APIs).
 * Patient login → /diario → save check-in → history; clinician cannot stay on /diario.
 */
const { test, expect } = require("@playwright/test");

const PATIENT = "550e8400-e29b-41d4-a716-446655440000";

/** Minimal JWT-shaped tokens (AuthContext only base64-decodes the payload segment). */
const PATIENT_JWT =
  "header.eyJzdWIiOiI1NTBlODQwMC1lMjliLTQxZDQtYTcxNi00NDY2NTU0NDAwMDAiLCJyb2xlIjoicGF0aWVudCJ9.signature";
const CLINICIAN_JWT =
  "header.eyJzdWIiOiJkZXYtY2xpbmljaWFuIiwicm9sZSI6ImNsaW5pY2lhbiJ9.signature";

async function mockPatientDevLogin(page) {
  await page.route("**/api/auth/dev-login", async (route) => {
    const body = route.request().postDataJSON() || {};
    if (body.role === "patient") {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          access_token: PATIENT_JWT,
          token_type: "bearer",
          role: "patient",
          sub: body.sub || PATIENT,
        }),
      });
      return;
    }
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
}

test("Sprint 12 patient diary: login, save check-in, see history", async ({ page }) => {
  await mockPatientDevLogin(page);

  let saved = false;
  await page.route(`**/api/rag/diary/patient/${PATIENT}**`, async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        items: saved
          ? [
              {
                entry_id: "dddddddd-dddd-4ddd-8ddd-dddddddddddd",
                entry_date: "2026-07-16",
                checkin: {
                  profile_version: "patient_diary_v0",
                  checkin_date: "2026-07-16",
                  pain_nrs_0_10: 4,
                  sleep_quality_0_10: 6,
                  mood_0_10: 7,
                  function_0_10: 5,
                  notes_es: "Me siento mejor",
                },
              },
            ]
          : [],
      }),
    });
  });

  await page.route("**/api/rag/diary", async (route) => {
    if (route.request().method() === "POST") {
      const req = route.request().postDataJSON();
      expect(req.patient_id).toBe(PATIENT);
      expect(req.checkin.pain_nrs_0_10).toBe(4);
      expect(req.checkin.notes_es).toBe("Me siento mejor");
      saved = true;
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          entry_id: "dddddddd-dddd-4ddd-8ddd-dddddddddddd",
          patient_id: PATIENT,
          entry_date: req.checkin.checkin_date,
          checkin: req.checkin,
        }),
      });
      return;
    }
    await route.fallback();
  });

  await page.goto("/login");
  await page.getByLabel("UUID de paciente (desarrollo)").fill(PATIENT);
  await page.getByRole("button", { name: "Entrar (desarrollo — paciente)" }).click();
  await expect(page).toHaveURL(/\/diario$/);
  await expect(page.getByRole("heading", { name: "Mi diario" })).toBeVisible();
  await expect(page.getByRole("code")).toHaveText(PATIENT);

  await page.getByLabel("Dolor 0–10").fill("4");
  await page.getByLabel("Sueño 0–10").fill("6");
  await page.getByLabel("Ánimo 0–10").fill("7");
  await page.getByLabel("Función 0–10").fill("5");
  await page.getByLabel("Notas (opcional)").fill("Me siento mejor");
  await page.getByRole("button", { name: "Guardar check-in" }).click();

  await expect(page.getByText("Check-in guardado.")).toBeVisible();
  await expect(page.getByText(/dolor 4/)).toBeVisible();
  await expect(page.getByText(/Me siento mejor/)).toBeVisible();
});

test("Sprint 12: clinician visiting /diario redirects to dashboard", async ({ page }) => {
  await mockPatientDevLogin(page);
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

  await page.goto("/diario");
  await expect(page).toHaveURL(/\/dashboard$/);
});

test("Sprint 12: patient visiting /dashboard redirects to /diario", async ({ page }) => {
  await mockPatientDevLogin(page);
  await page.route(`**/api/rag/diary/patient/${PATIENT}**`, async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({ items: [] }),
    });
  });

  await page.goto("/login");
  await page.getByLabel("UUID de paciente (desarrollo)").fill(PATIENT);
  await page.getByRole("button", { name: "Entrar (desarrollo — paciente)" }).click();
  await expect(page).toHaveURL(/\/diario$/);

  await page.goto("/dashboard");
  await expect(page).toHaveURL(/\/diario$/);
});
