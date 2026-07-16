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
  /** US-DIARY-AUTH-PROD — public invite redeem → patient JWT */
  redeemInvite: (payload) => api.post("/auth/redeem-invite", payload),
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

  /** US-INT-002 — intake risk flags for a saved profile */
  getIntakeRiskFlags: (patientId) => api.get(`/rag/intake/${patientId}/risk-flags`),

  /** Generate a treatment plan */
  generatePlan: (payload) => api.post("/rag/plan/generate", payload),

  /** Get a plan by ID */
  getPlan: (planId) => api.get(`/rag/plan/${planId}`),

  /** US-PLAN-004 — list approved-plan templates (memory bank) */
  listPlanMemoryBank: (params = {}) => api.get("/rag/plan/memory-bank", { params }),

  /** Save an approved plan snapshot into the memory bank */
  addPlanToMemoryBank: (payload) => api.post("/rag/plan/memory-bank", payload),

  /** Create a new pending_review plan from a memory-bank template */
  instantiatePlanMemoryBank: (templateId, payload) =>
    api.post(`/rag/plan/memory-bank/${templateId}/instantiate`, payload),

  /** Get source chunks for a plan */
  getPlanSources: (planId) => api.get(`/rag/plan/${planId}/sources`),

  /** Download approved plan as PDF */
  downloadPlanPdf: (planId) =>
    api.get(`/rag/plan/${planId}/pdf`, {
      responseType: "blob",
    }),

  /** US-DIARY-UI — clinician-proxy diary upsert */
  saveDiary: (payload) => api.post("/rag/diary", payload),

  /** US-DIARY-AUTH-PROD — create single-use patient invite */
  createDiaryInvite: (payload) => api.post("/rag/diary/invites", payload),

  /** List diary entries for a patient */
  listDiary: (patientId, params = {}) =>
    api.get(`/rag/diary/patient/${patientId}`, { params }),

  /** US-ANLY-UI — outcome trend series */
  getOutcomesTrend: (patientId, params = {}) =>
    api.get(`/rag/analytics/patient/${patientId}/outcomes-trend`, { params }),

  /** Plateau / worsening flags */
  getPlateauFlags: (patientId, params = {}) =>
    api.get(`/rag/analytics/patient/${patientId}/plateau-flags`, { params }),

  /** US-SESS-UI — create structured session log */
  createSession: (payload) => api.post("/rag/sessions", payload),

  /** List sessions for a patient */
  listSessions: (patientId, params = {}) =>
    api.get(`/rag/sessions/patient/${patientId}`, { params }),

  /** AI / heuristic session note suggestion */
  suggestSessionNote: (payload) => api.post("/rag/sessions/suggest-note", payload),

  /** US-PRED-001 — estimate short-term recovery trajectory from diary */
  getRecoveryTrajectory: (patientId, params = {}) =>
    api.get(`/rag/analytics/patient/${patientId}/recovery-trajectory`, { params }),

  /** US-PRED-002 — derive clinical recommendations from recovery trajectory */
  getRecoveryRecommendations: (patientId, params = {}) =>
    api.get(`/rag/analytics/patient/${patientId}/recovery-recommendations`, { params }),

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
