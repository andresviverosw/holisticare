#!/usr/bin/env node
/**
 * Quick smoke checks against a running HolistiCare API (no Docker required in CI).
 *
 * Usage (from repo root, API must be running):
 *   npm run smoke:api
 *   node scripts/smoke-api.mjs
 *   SMOKE_API_URL=http://127.0.0.1:8000 node scripts/smoke-api.mjs
 *
 * Steps:
 *   1. GET /health — expect 200 and { "status": "ok" }
 *   2. GET /rag/chunks?limit=1 — expect 200 (public browse endpoint)
 */

const base = (process.env.SMOKE_API_URL || "http://127.0.0.1:8000").replace(/\/$/, "");

async function assertOk(res, label) {
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`${label} failed: ${res.status} ${text.slice(0, 200)}`);
  }
}

async function main() {
  const health = await fetch(`${base}/health`);
  await assertOk(health, "GET /health");
  const healthJson = await health.json();
  if (healthJson.status !== "ok") {
    throw new Error(`GET /health: unexpected body ${JSON.stringify(healthJson)}`);
  }
  console.log("OK GET /health");

  const chunks = await fetch(`${base}/rag/chunks?limit=1`);
  await assertOk(chunks, "GET /rag/chunks");
  const chunksJson = await chunks.json();
  if (!chunksJson || typeof chunksJson !== "object" || !Array.isArray(chunksJson.items)) {
    throw new Error(`GET /rag/chunks: expected { items: [] }, got ${JSON.stringify(chunksJson).slice(0, 200)}`);
  }
  console.log("OK GET /rag/chunks");
  console.log(`Smoke complete against ${base}`);
}

main().catch((err) => {
  console.error(err.message || err);
  process.exit(1);
});
