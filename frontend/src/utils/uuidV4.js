/**
 * UUID helpers for patient identifiers.
 * - New patients: RFC-4122 UUID v4 (`newPatientUuid` / `isValidUuidV4`)
 * - Lookups (incl. SYNTH-01 uuid5): any RFC-4122 UUID (`isValidUuid`)
 */

const UUID_ANY =
  /^[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;

const UUID_V4 =
  /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;

/** Accepts any RFC-4122 UUID version (v1–v8), any casing; trims whitespace. */
export function isValidUuid(value) {
  if (typeof value !== "string") return false;
  return UUID_ANY.test(value.trim());
}

export function isValidUuidV4(value) {
  if (typeof value !== "string") return false;
  return UUID_V4.test(value.trim());
}

/** Returns a new RFC-4122 UUID v4 (uses global `crypto.randomUUID`). */
export function newPatientUuid() {
  const cryptoRef = globalThis.crypto;
  if (!cryptoRef || typeof cryptoRef.randomUUID !== "function") {
    throw new Error("crypto.randomUUID no está disponible en este entorno.");
  }
  return cryptoRef.randomUUID();
}
