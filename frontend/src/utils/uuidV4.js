/**
 * RFC-4122 UUID version 4 validation (matches backend Pydantic UUID4 expectations).
 * Accepts any casing; trims surrounding whitespace.
 */

const UUID_V4 =
  /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;

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
