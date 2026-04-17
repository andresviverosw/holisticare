import { isValidUuidV4 } from "./uuidV4";

export const RECENT_PATIENTS_STORAGE_KEY = "holisticare_recent_patients_v1";
export const RECENT_PATIENTS_MAX = 10;

/**
 * @typedef {{ id: string, label: string, savedAt: string }} RecentPatientEntry
 */

function safeParseList(raw) {
  if (!raw) return [];
  try {
    const data = JSON.parse(raw);
    return Array.isArray(data) ? data : [];
  } catch {
    return [];
  }
}

function normalizeEntry(entry) {
  if (!entry || typeof entry !== "object") return null;
  const id = typeof entry.id === "string" ? entry.id.trim() : "";
  if (!isValidUuidV4(id)) return null;
  const label = typeof entry.label === "string" ? entry.label.trim().slice(0, 120) : "";
  const savedAt = typeof entry.savedAt === "string" ? entry.savedAt : new Date().toISOString();
  return { id, label, savedAt };
}

/**
 * @param {Storage | null | undefined} storage
 * @returns {RecentPatientEntry[]}
 */
export function listRecentPatients(storage = typeof localStorage !== "undefined" ? localStorage : null) {
  if (!storage) return [];
  const raw = storage.getItem(RECENT_PATIENTS_STORAGE_KEY);
  const parsed = safeParseList(raw);
  const out = [];
  for (const item of parsed) {
    const n = normalizeEntry(item);
    if (n) out.push(n);
  }
  return out;
}

/**
 * Most recent first. Dedupes by `id`.
 * @param {RecentPatientEntry[]} list
 * @param {{ id: string, label?: string }} entry
 * @returns {RecentPatientEntry[]}
 */
export function mergeRecentPatientList(list, entry) {
  const n = normalizeEntry({ ...entry, savedAt: entry.savedAt || new Date().toISOString() });
  if (!n) return [...list];
  const rest = list.filter((x) => x.id !== n.id);
  return [n, ...rest].slice(0, RECENT_PATIENTS_MAX);
}

/**
 * @param {{ id: string, label?: string }} entry
 * @param {Storage} [storage]
 */
export function addRecentPatient(entry, storage = typeof localStorage !== "undefined" ? localStorage : null) {
  if (!storage) return;
  const n = normalizeEntry({ ...entry, savedAt: new Date().toISOString() });
  if (!n) return;
  const next = mergeRecentPatientList(listRecentPatients(storage), n);
  storage.setItem(RECENT_PATIENTS_STORAGE_KEY, JSON.stringify(next));
}
