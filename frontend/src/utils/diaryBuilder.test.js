import { describe, expect, it } from "vitest";
import { buildDiaryCheckin, validateDiaryForm } from "./diaryBuilder";

describe("validateDiaryForm", () => {
  it("requires checkin date and 0–10 scores", () => {
    expect(validateDiaryForm({})).toMatch(/fecha/i);
    expect(
      validateDiaryForm({
        checkinDate: "2026-07-16",
        pain: "11",
        sleep: "5",
        mood: "5",
        functionScore: "5",
      }),
    ).toMatch(/dolor/i);
    expect(
      validateDiaryForm({
        checkinDate: "2026-07-16",
        pain: "5",
        sleep: "5",
        mood: "5",
        functionScore: "5",
      }),
    ).toBeNull();
  });

  it("rejects notes longer than 1500 characters", () => {
    expect(
      validateDiaryForm({
        checkinDate: "2026-07-16",
        pain: "5",
        sleep: "5",
        mood: "5",
        functionScore: "5",
        notesEs: "x".repeat(1501),
      }),
    ).toMatch(/1500/);
  });
});

describe("buildDiaryCheckin", () => {
  it("builds patient_diary_v0 with optional notes_es", () => {
    expect(
      buildDiaryCheckin({
        checkinDate: "2026-07-16",
        pain: "7",
        sleep: "6",
        mood: "5",
        functionScore: "4",
        notesEs: "  Mejoró algo  ",
      }),
    ).toEqual({
      profile_version: "patient_diary_v0",
      checkin_date: "2026-07-16",
      pain_nrs_0_10: 7,
      sleep_quality_0_10: 6,
      mood_0_10: 5,
      function_0_10: 4,
      notes_es: "Mejoró algo",
    });
  });

  it("omits blank notes_es as null", () => {
    const payload = buildDiaryCheckin({
      checkinDate: "2026-07-16",
      pain: "1",
      sleep: "2",
      mood: "3",
      functionScore: "4",
      notesEs: "   ",
    });
    expect(payload.notes_es).toBeNull();
  });
});
