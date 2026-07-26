import { describe, expect, it } from "vitest";
import { resolveApiBaseUrl } from "./apiBaseUrl";

describe("resolveApiBaseUrl (US-OPS-SPA-HOST)", () => {
  it("uses VITE_API_BASE_URL when set", () => {
    expect(resolveApiBaseUrl("https://holisticare-api.onrender.com")).toBe(
      "https://holisticare-api.onrender.com",
    );
  });

  it("trims trailing slash from configured base URL", () => {
    expect(resolveApiBaseUrl("https://api.example.com/")).toBe("https://api.example.com");
  });

  it("falls back to /api when unset or empty", () => {
    expect(resolveApiBaseUrl(undefined)).toBe("/api");
    expect(resolveApiBaseUrl("")).toBe("/api");
    expect(resolveApiBaseUrl("   ")).toBe("/api");
  });
});
