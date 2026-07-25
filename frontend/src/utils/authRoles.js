/**
 * US-DIARY-UI-PATIENT — role predicates for SPA route eligibility.
 */
import { isValidUuidV4 } from "./uuidV4";

export function isClinicianRole(role) {
  return role === "clinician" || role === "admin";
}

export function isPatientRole(role) {
  return role === "patient";
}

export function canAccessClinicianRoutes({ isAuthenticated, role }) {
  return Boolean(isAuthenticated) && isClinicianRole(role);
}

export function canAccessPatientRoutes({ isAuthenticated, role, sub }) {
  return Boolean(isAuthenticated) && isPatientRole(role) && isValidUuidV4(sub || "");
}

/** Default post-login home for a JWT role. */
export function homePathForRole(role) {
  if (isPatientRole(role)) return "/diario";
  if (isClinicianRole(role)) return "/dashboard";
  return "/login";
}
