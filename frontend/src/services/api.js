import axios from "axios";

const TOKEN_KEY = "holisticare_token";

const api = axios.create({
  baseURL: "/api",
  headers: { "Content-Type": "application/json" },
});

export function getStoredToken() {
  return typeof localStorage !== "undefined" ? localStorage.getItem(TOKEN_KEY) : null;
}

export function setStoredToken(token) {
  if (typeof localStorage === "undefined") return;
  if (token) localStorage.setItem(TOKEN_KEY, token);
  else localStorage.removeItem(TOKEN_KEY);
}

api.interceptors.request.use((config) => {
  const t = getStoredToken();
  if (t) {
    config.headers.Authorization = `Bearer ${t}`;
  }
  return config;
});

// ─── Auth (development) ──────────────────────────────────────

export const authApi = {
  devLogin: (payload) => api.post("/auth/dev-login", payload),
};

// ─── RAG endpoints ────────────────────────────────────────────

export const ragApi = {
  /** Trigger ingestion pipeline (admin) */
  ingest: (sourceDir = "data/mock", forceReindex = false) =>
    api.post("/rag/ingest", { source_dir: sourceDir, force_reindex: forceReindex }),

  /** Browse indexed clinical chunks */
  listChunks: (params = {}) => api.get("/rag/chunks", { params }),

  /** Persist intake profile (generic_holistic_v0) */
  saveIntake: (payload) => api.post("/rag/intake", payload),

  /** Load persisted intake for a patient */
  getIntake: (patientId) => api.get(`/rag/intake/${patientId}`),

  /** Generate a treatment plan */
  generatePlan: (payload) => api.post("/rag/plan/generate", payload),

  /** Get a plan by ID */
  getPlan: (planId) => api.get(`/rag/plan/${planId}`),

  /** Get source chunks for a plan */
  getPlanSources: (planId) => api.get(`/rag/plan/${planId}/sources`),

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
