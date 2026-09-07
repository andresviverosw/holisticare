import { describe, expect, it, beforeEach, afterEach } from "vitest";
import { getStoredToken, setStoredToken } from "../services/api";
import { PWA_SESSION_TOKEN_KEY, readPersistedSessionToken } from "./pwaSession";

describe("US-MOB-002 pwaSession", () => {
  const memory = new Map();

  beforeEach(() => {
    memory.clear();
    globalThis.localStorage = {
      getItem: (k) => (memory.has(k) ? memory.get(k) : null),
      setItem: (k, v) => memory.set(k, String(v)),
      removeItem: (k) => memory.delete(k),
    };
  });

  afterEach(() => {
    delete globalThis.localStorage;
  });

  it("uses the same storage key as Auth/API so home-screen reopen keeps the JWT", () => {
    expect(PWA_SESSION_TOKEN_KEY).toBe("holisticare_token");
    setStoredToken("jwt-from-login");
    expect(readPersistedSessionToken()).toBe("jwt-from-login");
    expect(getStoredToken()).toBe("jwt-from-login");
  });

  it("clears predictable session state on logout-equivalent null token", () => {
    setStoredToken("jwt-from-login");
    setStoredToken(null);
    expect(readPersistedSessionToken()).toBeNull();
  });
});
