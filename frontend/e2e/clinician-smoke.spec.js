/* global require */
const { test, expect } = require("@playwright/test");

test("clinician can login, generate, and approve a plan", async ({ page }) => {
  const planId = "11111111-1111-4111-8111-111111111111";

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

  await page.route("**/api/rag/plan/generate", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        plan_id: planId,
        status: "pending_review",
        weeks: [
          {
            week: 1,
            goals: ["Reducir dolor"],
            therapies: [
              {
                type: "fisioterapia",
                frequency: "3/semana",
                duration_minutes: 45,
                rationale: "Movilidad y fortalecimiento progresivo.",
                citations: ["REF-001"],
              },
            ],
            contraindications_flagged: [],
            outcome_checkpoints: ["Dolor NRS <= 5"],
          },
        ],
        citations_used: ["REF-001"],
        insufficient_evidence: false,
      }),
    });
  });

  await page.route(`**/api/rag/plan/${planId}`, async (route) => {
    if (route.request().method() === "GET") {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          plan_id: planId,
          status: "pending_review",
          weeks: [
            {
              week: 1,
              goals: ["Reducir dolor"],
              therapies: [
                {
                  type: "fisioterapia",
                  frequency: "3/semana",
                  duration_minutes: 45,
                  rationale: "Movilidad y fortalecimiento progresivo.",
                  citations: ["REF-001"],
                },
              ],
              contraindications_flagged: [],
              outcome_checkpoints: ["Dolor NRS <= 5"],
            },
          ],
          citations_used: ["REF-001"],
        }),
      });
      return;
    }

    await route.fallback();
  });

  await page.route(`**/api/rag/plan/${planId}/approve`, async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        plan_id: planId,
        status: "approved",
      }),
    });
  });

  await page.goto("/login");
  await page.getByRole("button", { name: "Entrar (desarrollo — clínico)" }).click();
  await expect(page).toHaveURL(/\/dashboard$/);

  await page.getByRole("button", { name: "Nuevo paciente" }).click();
  await page.getByRole("button", { name: "Generar plan IA" }).click();

  await expect(page).toHaveURL(new RegExp(`/plan/${planId}$`));
  await expect(page.getByRole("heading", { name: "Revisión del plan" })).toBeVisible();
  await expect(page.getByText("REF-001").first()).toBeVisible();

  await page.getByRole("button", { name: "✓ Aprobar plan" }).click();
  await expect(page.getByText("Plan aprobado y vinculado al expediente del paciente.")).toBeVisible();
});

test("dashboard shows error when plan generation fails", async ({ page }) => {
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

  await page.route("**/api/rag/plan/generate", async (route) => {
    await route.fulfill({
      status: 500,
      contentType: "application/json",
      body: JSON.stringify({ detail: "Temporary upstream failure" }),
    });
  });

  await page.goto("/login");
  await page.getByRole("button", { name: "Entrar (desarrollo — clínico)" }).click();
  await expect(page).toHaveURL(/\/dashboard$/);

  await page.getByRole("button", { name: "Nuevo paciente" }).click();
  await page.getByRole("button", { name: "Generar plan IA" }).click();

  await expect(page.getByText("Request failed with status code 500")).toBeVisible();
  await expect(page).toHaveURL(/\/dashboard$/);
});
