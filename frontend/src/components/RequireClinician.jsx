import { Navigate, Outlet, useLocation } from "react-router";
import { useAuth } from "../context/AuthContext";
import { canAccessClinicianRoutes, homePathForRole } from "../utils/authRoles";

/**
 * Clinician/admin SPA shell. Patients are redirected to `/diario`.
 */
export default function RequireClinician() {
  const { isAuthenticated, role } = useAuth();
  const location = useLocation();

  if (!isAuthenticated) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }

  if (!canAccessClinicianRoutes({ isAuthenticated, role })) {
    return <Navigate to={homePathForRole(role)} replace />;
  }

  return <Outlet />;
}
