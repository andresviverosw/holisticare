/** US-MOB-002 — session continuity for home-screen / standalone reopen. */

import { AUTH_TOKEN_STORAGE_KEY, getStoredToken } from "../services/api";

export const PWA_SESSION_TOKEN_KEY = AUTH_TOKEN_STORAGE_KEY;

export function readPersistedSessionToken() {
  return getStoredToken();
}
