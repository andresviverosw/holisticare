import { describe, expect, it } from "vitest";
import { buildIntakePayload, parseCsvList, validateIntakeForm } from "./intakeBuilder";

describe("parseCsvList", () => {
  it("splits, trims and removes empty values", () => {
    expect(parseCsvList("a,  b ,, c ")).toEqual(["a", "b", "c"]);
  });
});

describe("validateIntakeForm", () => {
  it("requires chief complaint", () => {
    const err = validateIntakeForm({
      chiefComplaint: "  ",
      conditions: "lumbalgia",
      goals: "reducir dolor",
    });
    expect(err).toContain("motivo principal");
  });

  it("requires at least one condition and one goal", () => {
    expect(
      validateIntakeForm({
        chiefComplaint: "dolor lumbar",
        conditions: " , ",
        goals: "movilidad",
      }),
    ).toContain("condición");

    expect(
      validateIntakeForm({
        chiefComplaint: "dolor lumbar",
        conditions: "lumbalgia",
        goals: "",
      }),
    ).toContain("objetivo");
  });
});

describe("buildIntakePayload", () => {
  it("maps form fields to generic_holistic_v0", () => {
    const payload = buildIntakePayload({
      ageRange: "40-50",
      sexAtBirth: "F",
      chiefComplaint: "Dolor lumbar",
      conditions: "lumbalgia, ciática",
      goals: "reducir dolor, mejorar movilidad",
      contraindications: "",
      currentMedications: "ibuprofeno",
      allergies: "",
      baselinePain: "7",
      baselineNotes: "función limitada",
      psychosocialSummary: "",
      priorInterventions: "fisioterapia",
    });

    expect(payload.profile_version).toBe("generic_holistic_v0");
    expect(payload.conditions).toEqual(["lumbalgia", "ciática"]);
    expect(payload.goals).toEqual(["reducir dolor", "mejorar movilidad"]);
    expect(payload.baseline_outcomes).toEqual({
      pain_nrs_0_10: 7,
      notes: "función limitada",
    });
  });
});

