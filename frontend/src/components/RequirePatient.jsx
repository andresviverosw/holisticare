import { Navigate, Outlet, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { canAccessPatientRoutes, homePathForRole } from "../utils/authRoles";

/**
 * US-DIARY-UI-PATIENT — patient-only routes (`/diario`).
 * Clinicians/admins are redirected to `/dashboard`.
 */
export default function RequirePatient() {
  const { isAuthenticated, role, sub } = useAuth();
  const location = useLocation();

  if (!isAuthenticated) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }

  if (!canAccessPatientRoutes({ isAuthenticated, role, sub })) {
    return <Navigate to={homePathForRole(role)} replace />;
  }

  return <Outlet />;
}
