import { describe, expect, it } from "vitest";
import {
  canAccessClinicianRoutes,
  canAccessPatientRoutes,
  homePathForRole,
  isClinicianRole,
  isPatientRole,
} from "./authRoles";

const PATIENT = "550e8400-e29b-41d4-a716-446655440000";

describe("authRoles", () => {
  it("classifies clinician and admin as clinician roles", () => {
    expect(isClinicianRole("clinician")).toBe(true);
    expect(isClinicianRole("admin")).toBe(true);
    expect(isClinicianRole("patient")).toBe(false);
    expect(isPatientRole("patient")).toBe(true);
    expect(isPatientRole("clinician")).toBe(false);
  });

  it("gates clinician routes to authenticated clinician/admin only", () => {
    expect(canAccessClinicianRoutes({ isAuthenticated: true, role: "clinician" })).toBe(true);
    expect(canAccessClinicianRoutes({ isAuthenticated: true, role: "admin" })).toBe(true);
    expect(canAccessClinicianRoutes({ isAuthenticated: true, role: "patient" })).toBe(false);
    expect(canAccessClinicianRoutes({ isAuthenticated: false, role: "clinician" })).toBe(false);
  });

  it("gates patient routes to patient role + UUID v4 sub", () => {
    expect(
      canAccessPatientRoutes({ isAuthenticated: true, role: "patient", sub: PATIENT }),
    ).toBe(true);
    expect(
      canAccessPatientRoutes({ isAuthenticated: true, role: "patient", sub: "not-uuid" }),
    ).toBe(false);
    expect(
      canAccessPatientRoutes({ isAuthenticated: true, role: "clinician", sub: PATIENT }),
    ).toBe(false);
    expect(
      canAccessPatientRoutes({ isAuthenticated: false, role: "patient", sub: PATIENT }),
    ).toBe(false);
  });

  it("maps roles to home paths", () => {
    expect(homePathForRole("patient")).toBe("/diario");
    expect(homePathForRole("clinician")).toBe("/dashboard");
    expect(homePathForRole("admin")).toBe("/dashboard");
    expect(homePathForRole(null)).toBe("/login");
  });
});
