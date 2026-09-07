/* global require */
const { test, expect } = require("@playwright/test");

const IPHONE_VIEWPORT = { width: 390, height: 844 };
const PLAN_ID = "22222222-2222-4222-8222-222222222222";

function stubAuthAndPlan(page, { status = "pending_review" } = {}) {
  return (async () => {
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

    await page.route(`**/api/rag/plan/${PLAN_ID}`, async (route) => {
      if (route.request().method() !== "GET") {
        await route.fallback();
        return;
      }
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          plan_id: PLAN_ID,
          status,
          requires_practitioner_review: true,
          confidence_note: "Borrador sintético para revisión móvil.",
          citations_used: ["REF-MOBILE01"],
          weeks: [
            {
              week: 1,
              goals: ["Reducir dolor"],
              therapies: [
                {
                  type: "Fisioterapia",
                  frequency: "2x/semana",
                  duration_minutes: 45,
                  rationale: "Movilidad lumbar",
                  citations: ["REF-MOBILE01"],
                },
              ],
              contraindications_flagged: [],
              outcome_checkpoints: ["pain_nrs_0_10"],
            },
          ],
          retrieval_metadata: {
            queries_used: ["q1"],
            candidates_retrieved: 4,
            chunks_passed_to_llm: 2,
            reranker_backend: "passthrough",
          },
        }),
      });
    });
  })();
}

test.describe("US-MOB-003 mobile plan decision gate", () => {
  test("approve with notes from iPhone viewport", async ({ page }) => {
    await page.setViewportSize(IPHONE_VIEWPORT);
    await stubAuthAndPlan(page);

    let approveBody = null;
    await page.route(`**/api/rag/plan/${PLAN_ID}/approve`, async (route) => {
      approveBody = route.request().postDataJSON();
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ plan_id: PLAN_ID, status: "approved" }),
      });
    });

    await page.goto("/login");
    await page.getByRole("button", { name: "Entrar (desarrollo — clínico)" }).click();
    await expect(page).toHaveURL(/\/dashboard$/);

    await page.goto(`/plan/${PLAN_ID}`);
    await expect(page.getByRole("heading", { name: /Revisión del plan/i })).toBeVisible();
    await expect(page.getByText("REF-MOBILE01").first()).toBeVisible();
    await expect(page.getByText(/pending review/i).first()).toBeVisible();

    const gate = page.getByTestId("plan-decision-gate");
    await expect(gate).toBeVisible();

    const approveBtn = gate.getByRole("button", { name: /Aprobar plan/i });
    const box = await approveBtn.boundingBox();
    expect(box).toBeTruthy();
    expect(box.width).toBeGreaterThan(200);
    expect(box.height).toBeGreaterThanOrEqual(40);

    await gate.getByLabel(/Notas del practicante/i).fill("Aprobado en consulta móvil.");
    await approveBtn.click();

    await expect(page.getByRole("status")).toContainText(/Plan aprobado/i);
    expect(approveBody).toMatchObject({
      action: "approve",
      practitioner_notes: "Aprobado en consulta móvil.",
    });
  });

  test("reject shows clear failure path feedback", async ({ page }) => {
    await page.setViewportSize(IPHONE_VIEWPORT);
    await stubAuthAndPlan(page);

    await page.route(`**/api/rag/plan/${PLAN_ID}/approve`, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ plan_id: PLAN_ID, status: "rejected" }),
      });
    });

    await page.goto("/login");
    await page.getByRole("button", { name: "Entrar (desarrollo — clínico)" }).click();
    await expect(page).toHaveURL(/\/dashboard$/);
    await page.goto(`/plan/${PLAN_ID}`);
    await expect(page.getByRole("heading", { name: /Revisión del plan/i })).toBeVisible();

    const gate = page.getByTestId("plan-decision-gate");
    await expect(gate).toBeVisible({ timeout: 10000 });
    await gate.getByRole("button", { name: /Rechazar/i }).click();
    await expect(page.getByRole("status")).toContainText(/Plan rechazado/i);
  });
});
