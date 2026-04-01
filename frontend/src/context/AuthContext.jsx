import { createContext, useContext, useMemo, useState, useCallback, useEffect } from "react";
import { authApi, getStoredToken, setStoredToken } from "../services/api";

const AuthContext = createContext(null);

function decodeJwtPayload(token) {
  if (!token || typeof token !== "string") return {};
  try {
    const part = token.split(".")[1];
    if (!part) return {};
    const json = atob(part.replace(/-/g, "+").replace(/_/g, "/"));
    return JSON.parse(json);
  } catch {
    return {};
  }
}

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => getStoredToken());

  useEffect(() => {
    setStoredToken(token);
  }, [token]);

  const logout = useCallback(() => setToken(null), []);

  const loginWithToken = useCallback((accessToken) => {
    setToken(accessToken);
  }, []);

  const loginDevClinician = useCallback(async (role = "clinician", sub = "dev-clinician") => {
    const res = await authApi.devLogin({ role, sub });
    setToken(res.data.access_token);
    return res.data;
  }, []);

  const claims = useMemo(() => decodeJwtPayload(token), [token]);
  const role = claims.role || null;
  const sub = claims.sub || null;
  const isAuthenticated = Boolean(token);

  const value = useMemo(
    () => ({
      token,
      role,
      sub,
      isAuthenticated,
      loginWithToken,
      loginDevClinician,
      logout,
    }),
    [token, role, sub, isAuthenticated, loginWithToken, loginDevClinician, logout],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth debe usarse dentro de AuthProvider");
  return ctx;
}
