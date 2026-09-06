import { describe, expect, it } from "vitest";
import {
  COLD_START_HINT_MS,
  COLD_START_HINT_TEXT,
  shouldShowColdStartHint,
} from "./coldStartFeedback";

describe("coldStartFeedback (US-UX-COLDSTART-001)", () => {
  it("exposes a multi-second threshold for Render free-tier wake", () => {
    expect(COLD_START_HINT_MS).toBeGreaterThanOrEqual(2000);
    expect(COLD_START_HINT_MS).toBeLessThanOrEqual(5000);
  });

  it("hides the hint until the threshold is reached", () => {
    expect(shouldShowColdStartHint(0, COLD_START_HINT_MS)).toBe(false);
    expect(shouldShowColdStartHint(COLD_START_HINT_MS - 1, COLD_START_HINT_MS)).toBe(false);
  });

  it("shows the hint once elapsed time meets the threshold", () => {
    expect(shouldShowColdStartHint(COLD_START_HINT_MS, COLD_START_HINT_MS)).toBe(true);
    expect(shouldShowColdStartHint(COLD_START_HINT_MS + 10_000, COLD_START_HINT_MS)).toBe(true);
  });

  it("provides Spanish copy that mentions cold start / API wake", () => {
    expect(COLD_START_HINT_TEXT.toLowerCase()).toMatch(/api|servidor|despert/);
  });
});
