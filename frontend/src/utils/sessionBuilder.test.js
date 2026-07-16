import { describe, expect, it } from "vitest";
import {
  buildNoteAssistPayload,
  buildSessionLog,
  validateSessionForm,
} from "./sessionBuilder";

const baseForm = {
  sessionAt: "2026-07-16T10:30",
  interventions: [{ therapyType: "acupuntura", description: "Puntos locales", durationMinutes: "45" }],
  observations: "Buena tolerancia",
  patientReportedResponse: "",
};

describe("validateSessionForm", () => {
  it("requires session time, one intervention, and observations", () => {
    expect(validateSessionForm({ ...baseForm, sessionAt: "" })).toMatch(/fecha|hora/i);
    expect(validateSessionForm({ ...baseForm, interventions: [] })).toMatch(/intervención/i);
    expect(
      validateSessionForm({
        ...baseForm,
        interventions: [{ therapyType: "  ", description: "x", durationMinutes: "" }],
      }),
    ).toMatch(/intervención/i);
    expect(validateSessionForm({ ...baseForm, observations: "  " })).toMatch(/observacion/i);
    expect(validateSessionForm(baseForm)).toBeNull();
  });
});

describe("buildSessionLog", () => {
  it("builds clinical_session_v0", () => {
    expect(buildSessionLog(baseForm)).toEqual({
      profile_version: "clinical_session_v0",
      session_at: "2026-07-16T10:30:00",
      interventions: [
        {
          therapy_type: "acupuntura",
          description: "Puntos locales",
          duration_minutes: 45,
        },
      ],
      observations: "Buena tolerancia",
      patient_reported_response: null,
    });
  });
});

describe("buildNoteAssistPayload", () => {
  it("builds clinical_session_note_assist_v0 from interventions", () => {
    expect(buildNoteAssistPayload(baseForm)).toEqual({
      profile_version: "clinical_session_note_assist_v0",
      interventions: [
        {
          therapy_type: "acupuntura",
          description: "Puntos locales",
          duration_minutes: 45,
        },
      ],
      observations_draft: "Buena tolerancia",
      patient_reported_response: null,
    });
  });
});
