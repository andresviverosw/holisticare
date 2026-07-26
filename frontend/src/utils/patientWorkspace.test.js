import { describe, expect, it } from "vitest";
import {
  createClearedPatientDerivedState,
  createClearedPatientResultPanels,
  DEFAULT_INTAKE_FORM,
  defaultDiaryForm,
  defaultSessionForm,
} from "./patientWorkspace";

describe("createClearedPatientDerivedState", () => {
  it("resets lists and prediction panels so prior patient data cannot leak", () => {
    const now = new Date("2026-07-26T15:00:00.000Z");
    const cleared = createClearedPatientDerivedState(now);

    expect(cleared.diaryItems).toEqual([]);
    expect(cleared.sessionItems).toEqual([]);
    expect(cleared.outcomeRows).toEqual([]);
    expect(cleared.plateauView).toBeNull();
    expect(cleared.predictionResult).toBeNull();
    expect(cleared.recommendationResult).toBeNull();
    expect(cleared.riskFlags).toBeNull();
    expect(cleared.inviteLink).toBeNull();
    expect(cleared.intakeForm).toEqual(DEFAULT_INTAKE_FORM);
    expect(cleared.diaryForm).toEqual(defaultDiaryForm(now));
    expect(cleared.sessionForm).toEqual(defaultSessionForm(now));
  });

  it("returns a fresh intake object (not the shared default reference)", () => {
    const a = createClearedPatientDerivedState();
    const b = createClearedPatientDerivedState();
    a.intakeForm.chiefComplaint = "mutated";
    expect(b.intakeForm.chiefComplaint).toBe(DEFAULT_INTAKE_FORM.chiefComplaint);
  });
});

describe("createClearedPatientResultPanels", () => {
  it("clears bound panels without resetting intake/diary/session draft forms", () => {
    const panels = createClearedPatientResultPanels();
    expect(panels.diaryItems).toEqual([]);
    expect(panels.predictionResult).toBeNull();
    expect(panels).not.toHaveProperty("intakeForm");
    expect(panels).not.toHaveProperty("diaryForm");
    expect(panels).not.toHaveProperty("sessionForm");
  });
});
