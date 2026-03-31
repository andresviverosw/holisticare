import axios from "axios";

const api = axios.create({
  baseURL: "/api",
  headers: { "Content-Type": "application/json" },
});

// ─── RAG endpoints ────────────────────────────────────────────

export const ragApi = {
  /** Trigger ingestion pipeline (admin) */
  ingest: (sourceDir = "data/mock", forceReindex = false) =>
    api.post("/rag/ingest", { source_dir: sourceDir, force_reindex: forceReindex }),

  /** Browse indexed clinical chunks */
  listChunks: (params = {}) =>
    api.get("/rag/chunks", { params }),

  /** Generate a treatment plan */
  generatePlan: (payload) =>
    api.post("/rag/plan/generate", payload),

  /** Get a plan by ID */
  getPlan: (planId) =>
    api.get(`/rag/plan/${planId}`),

  /** Get source chunks for a plan */
  getPlanSources: (planId) =>
    api.get(`/rag/plan/${planId}/sources`),

  /** Approve or reject a plan */
  approvePlan: (planId, action, notes = null, editedPlan = null) =>
    api.patch(`/rag/plan/${planId}/approve`, {
      action,
      practitioner_notes: notes,
      edited_plan_json: editedPlan,
    }),
};

// ─── Health check ─────────────────────────────────────────────

export const healthCheck = () => api.get("/health");

export default api;
