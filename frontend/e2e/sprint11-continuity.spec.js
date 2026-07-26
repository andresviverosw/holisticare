/* global require */
/**
 * Sprint 11 QA — continuity panels smoke (mocked APIs).
 * Covers US-INT-002-UI, US-DIARY-UI, US-ANLY-UI, US-SESS-UI happy/empty/error paths.
 */
const { test, expect } = require("@playwright/test");

const PATIENT = "550e8400-e29b-41d4-a716-446655440000";

async function loginAndOpenDashboard(page) {
  // Register first so later test-specific routes take precedence (Playwright: last match wins).
  // Keeps Dashboard patient auto-reload off the missing backend in e2e.
  await page.route("**/api/rag/**", async (route) => {
    const url = route.request().url();
    const method = route.request().method();
    if (method === "GET" && url.includes("/plan/memory-bank")) {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ items: [] }),
      });
      return;
    }
    if (method === "GET" && url.includes("/risk-flags")) {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ risk_flags: [] }),
      });
      return;
    }
    if (method === "GET" && url.includes("/outcomes-trend")) {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ series: [] }),
      });
      return;
    }
    if (method === "GET" && url.includes("/plateau-flags")) {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ analysis_status: "insufficient_data", flags: [] }),
      });
      return;
    }
    if (method === "GET" && url.includes("/recovery-trajectory")) {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          analysis_status: "insufficient_data",
          reason: "Se requieren al menos 5 registros con dolor para estimar trayectoria.",
          trajectory: null,
        }),
      });
      return;
    }
    if (method === "GET" && url.includes("/recovery-recommendations")) {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          recommendation_status: "insufficient_data",
          recommendations: [],
          safety_notes: [],
          prediction: { analysis_status: "insufficient_data", trajectory: null },
        }),
      });
      return;
    }
    if (method === "GET" && (url.includes("/diary/patient/") || url.includes("/sessions/patient/"))) {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ items: [] }),
      });
      return;
    }
    if (method === "GET" && /\/rag\/intake\/[^/?]+$/.test(new URL(url).pathname.replace(/^\/api/, ""))) {
      await route.fulfill({ status: 404, contentType: "application/json", body: "{}" });
      return;
    }
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: "{}",
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

  await page.goto("/login");
  await page.getByRole("button", { name: "Entrar (desarrollo — clínico)" }).click();
  await expect(page).toHaveURL(/\/dashboard$/);
}

function patientIdInput(page) {
  return page.getByPlaceholder("Genera un ID nuevo o pega un UUID existente");
}

test("Sprint 11 continuity: risk flags, diary, progress, session", async ({ page }) => {
  await loginAndOpenDashboard(page);

  await page.route(`**/api/rag/intake/${PATIENT}/risk-flags`, async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        patient_id: PATIENT,
        risk_flags: [
          {
            code: "CONTRAINDICATION_DECLARED",
            severity: "high",
            message: "Se detectaron contraindicaciones declaradas en la historia clínica.",
          },
        ],
      }),
    });
  });

  await page.route("**/api/rag/diary", async (route) => {
    if (route.request().method() === "POST") {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          entry_id: "dddddddd-dddd-4ddd-8ddd-dddddddddddd",
          patient_id: PATIENT,
          entry_date: "2026-07-16",
          checkin: {
            profile_version: "patient_diary_v0",
            checkin_date: "2026-07-16",
            pain_nrs_0_10: 5,
            sleep_quality_0_10: 5,
            mood_0_10: 5,
            function_0_10: 5,
            notes_es: null,
          },
        }),
      });
      return;
    }
    await route.fallback();
  });

  await page.route(`**/api/rag/diary/patient/${PATIENT}**`, async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        patient_id: PATIENT,
        items: [
          {
            entry_id: "dddddddd-dddd-4ddd-8ddd-dddddddddddd",
            patient_id: PATIENT,
            entry_date: "2026-07-16",
            checkin: {
              pain_nrs_0_10: 5,
              sleep_quality_0_10: 5,
              mood_0_10: 5,
              function_0_10: 5,
            },
          },
        ],
        limit: 14,
        offset: 0,
      }),
    });
  });

  await page.route(`**/api/rag/analytics/patient/${PATIENT}/outcomes-trend**`, async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        patient_id: PATIENT,
        source: "patient_diary_v0",
        series: [
          {
            date: "2026-07-16",
            pain_nrs_0_10: 5,
            sleep_quality_0_10: 5,
            mood_0_10: 5,
            function_0_10: 5,
          },
        ],
      }),
    });
  });

  await page.route(`**/api/rag/analytics/patient/${PATIENT}/plateau-flags**`, async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        patient_id: PATIENT,
        analysis_status: "insufficient_data",
        flags: [],
      }),
    });
  });

  await page.route(`**/api/rag/analytics/patient/${PATIENT}/recovery-trajectory**`, async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        patient_id: PATIENT,
        analysis_status: "insufficient_data",
        reason: "Se requieren al menos 5 registros con dolor para estimar trayectoria.",
        trajectory: null,
        data_points_used: 1,
      }),
    });
  });

  await page.route(`**/api/rag/analytics/patient/${PATIENT}/recovery-recommendations**`, async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        patient_id: PATIENT,
        recommendation_status: "insufficient_data",
        reason: "Se requieren al menos 5 registros con dolor para estimar trayectoria.",
        recommendations: [],
        safety_notes: [],
        prediction: {
          analysis_status: "insufficient_data",
          reason: "Se requieren al menos 5 registros con dolor para estimar trayectoria.",
          trajectory: null,
        },
      }),
    });
  });

  await page.route(`**/api/rag/intake/${PATIENT}`, async (route) => {
    if (route.request().method() === "GET") {
      await route.fulfill({ status: 404, contentType: "application/json", body: "{}" });
      return;
    }
    await route.fallback();
  });

  await page.route("**/api/rag/sessions/suggest-note", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        profile_version: "clinical_session_note_assist_v0",
        suggested_observations:
          "Se realizó la sesión con las siguientes intervenciones: fisioterapia: Movilización.",
        suggested_patient_reported_response: "Paciente refiere tolerancia adecuada.",
      }),
    });
  });

  await page.route("**/api/rag/sessions", async (route) => {
    if (route.request().method() === "POST") {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          session_id: "ssssssss-ssss-4sss-8sss-ssssssssssss",
          patient_id: PATIENT,
          occurred_at: "2026-07-16T10:30:00",
          session_log: {
            interventions: [{ therapy_type: "fisioterapia", description: "Movilización" }],
          },
        }),
      });
      return;
    }
    await route.fallback();
  });

  await page.route(`**/api/rag/sessions/patient/${PATIENT}**`, async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        patient_id: PATIENT,
        items: [
          {
            session_id: "ssssssss-ssss-4sss-8sss-ssssssssssss",
            occurred_at: "2026-07-16T10:30:00",
            session_log: {
              interventions: [{ therapy_type: "fisioterapia", description: "Movilización" }],
            },
          },
        ],
        limit: 20,
        offset: 0,
      }),
    });
  });

  await patientIdInput(page).fill(PATIENT);

  // US-INT-002-UI
  await page.getByRole("button", { name: "Ver riesgos" }).click();
  await expect(page.getByText("Se detectaron contraindicaciones declaradas")).toBeVisible();
  await expect(page.getByRole("button", { name: "Generar plan IA" })).toBeEnabled();

  // US-DIARY-UI
  await expect(page.getByText("Registro de diario (practicante)")).toBeVisible();
  await page.getByRole("button", { name: "Guardar check-in" }).click();
  await expect(page.getByText("Check-in de diario guardado")).toBeVisible();
  await expect(page.getByText(/dolor 5/)).toBeVisible();

  // US-ANLY-UI — chart replaces tabular series (scope to Progreso; prediction panels share "datos insuficientes")
  const progressSection = page.locator("section").filter({ hasText: "Progreso (US-ANLY-UI)" });
  await progressSection.getByRole("button", { name: "Cargar progreso" }).click();
  await expect(progressSection.getByText("Estado: datos insuficientes")).toBeVisible();
  await expect(progressSection.getByTestId("outcome-trend-chart")).toBeVisible();
  await expect(progressSection.getByTestId("outcome-trend-chart").getByText("2026-07-16")).toBeVisible();

  // US-SESS-UI — fill description in session section
  const sessionHeading = page.getByText("Sesión clínica (US-SESS-UI)");
  await sessionHeading.scrollIntoViewIfNeeded();
  await page.getByLabel("Descripción", { exact: true }).fill("Movilización");
  await page.getByRole("button", { name: "Sugerir nota" }).click();
  await expect(page.getByText("Sugerencia de nota aplicada")).toBeVisible();
  await page.getByRole("button", { name: "Guardar sesión" }).click();
  await expect(page.getByText("Sesión registrada.")).toBeVisible();
  await expect(page.getByText(/10:30:00 — fisioterapia/)).toBeVisible();
});

test("Sprint 11 risk flags empty state does not block generate", async ({ page }) => {
  await loginAndOpenDashboard(page);

  await page.route(`**/api/rag/intake/${PATIENT}/risk-flags`, async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({ patient_id: PATIENT, risk_flags: [] }),
    });
  });

  await patientIdInput(page).fill(PATIENT);
  await page.getByRole("button", { name: "Ver riesgos" }).click();
  await expect(page.getByText("Sin banderas de riesgo")).toBeVisible();
  await expect(page.getByRole("button", { name: "Generar plan IA" })).toBeEnabled();
});

test("Sprint 11 risk flags 404 shows actionable error; generate stays available", async ({ page }) => {
  await loginAndOpenDashboard(page);

  await page.route(`**/api/rag/intake/${PATIENT}/risk-flags`, async (route) => {
    await route.fulfill({
      status: 404,
      contentType: "application/json",
      body: JSON.stringify({ detail: "Intake not found" }),
    });
  });

  await patientIdInput(page).fill(PATIENT);
  await page.getByRole("button", { name: "Ver riesgos" }).click();
  await expect(page.getByText(/No encontrado \(404\)/)).toBeVisible();
  await expect(page.getByRole("button", { name: "Generar plan IA" })).toBeEnabled();
});
