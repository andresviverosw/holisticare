import { Navigate, Outlet, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

/**
 * Clinician-only SPA: any authenticated JWT is allowed (role patient would still work
 * if pasted, but flows are intended for clinician/admin).
 */
export default function RequireClinician() {
  const { isAuthenticated } = useAuth();
  const location = useLocation();

  if (!isAuthenticated) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }

  return <Outlet />;
}
