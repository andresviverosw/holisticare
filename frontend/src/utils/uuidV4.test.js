import { describe, expect, it } from "vitest";
import { isValidUuid, isValidUuidV4, newPatientUuid } from "./uuidV4";

describe("isValidUuid", () => {
  it("accepts synthetic uuid5 patient ids", () => {
    expect(isValidUuid("be2ecd39-2ac6-5a8b-84af-b22f8fa7a4a8")).toBe(true);
  });

  it("accepts uuid v4", () => {
    expect(isValidUuid("550e8400-e29b-41d4-a716-446655440000")).toBe(true);
  });

  it("rejects malformed strings", () => {
    expect(isValidUuid("")).toBe(false);
    expect(isValidUuid("not-a-uuid")).toBe(false);
  });
});

describe("isValidUuidV4", () => {
  it("accepts a canonical lowercase v4 UUID", () => {
    expect(isValidUuidV4("550e8400-e29b-41d4-a716-446655440000")).toBe(true);
  });

  it("accepts uppercase and trims whitespace", () => {
    expect(isValidUuidV4("  550E8400-E29B-41D4-A716-446655440000  ")).toBe(true);
  });

  it("rejects non-version-4 UUIDs", () => {
    expect(isValidUuidV4("6ba7b810-9dad-11d1-80b4-00c04fd430c8")).toBe(false);
    expect(isValidUuidV4("be2ecd39-2ac6-5a8b-84af-b22f8fa7a4a8")).toBe(false);
  });

  it("rejects malformed strings", () => {
    expect(isValidUuidV4("")).toBe(false);
    expect(isValidUuidV4("not-a-uuid")).toBe(false);
    expect(isValidUuidV4(null)).toBe(false);
  });
});

describe("newPatientUuid", () => {
  it("returns a string that passes isValidUuidV4", () => {
    const id = newPatientUuid();
    expect(typeof id).toBe("string");
    expect(isValidUuidV4(id)).toBe(true);
  });
});
