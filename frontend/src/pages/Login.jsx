import { useState } from "react";
import { Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { formatApiError } from "../utils/apiErrors";
import { homePathForRole } from "../utils/authRoles";
import { isValidUuidV4 } from "../utils/uuidV4";

export default function Login() {
  const { isAuthenticated, role, loginDevClinician, loginDevPatient, loginWithToken } = useAuth();

  const [manualToken, setManualToken] = useState("");
  const [patientUuid, setPatientUuid] = useState("");
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const [patientLoading, setPatientLoading] = useState(false);

  if (isAuthenticated) {
    return <Navigate to={homePathForRole(role)} replace />;
  }

  async function handleDevLogin() {
    setLoading(true);
    setError(null);
    try {
      await loginDevClinician("clinician", "dev-clinician");
    } catch (err) {
      setError(
        formatApiError(err, {
          fallback:
            "No se pudo obtener el token de desarrollo. ¿Está ALLOW_DEV_AUTH habilitado en el backend?",
        }),
      );
    } finally {
      setLoading(false);
    }
  }

  async function handlePatientDevLogin(e) {
    e.preventDefault();
    setPatientLoading(true);
    setError(null);
    const uuid = patientUuid.trim();
    if (!isValidUuidV4(uuid)) {
      setError("Pegue un UUID versión 4 de paciente válido (el mismo que usa el clínico).");
      setPatientLoading(false);
      return;
    }
    try {
      await loginDevPatient(uuid);
    } catch (err) {
      setError(
        formatApiError(err, {
          fallback:
            err?.message ||
            "No se pudo iniciar sesión como paciente. ¿Está ALLOW_DEV_AUTH habilitado?",
        }),
      );
    } finally {
      setPatientLoading(false);
    }
  }

  function handleManualSubmit(e) {
    e.preventDefault();
    setError(null);
    const t = manualToken.trim();
    if (!t) {
      setError("Pegue un token JWT válido.");
      return;
    }
    loginWithToken(t);
  }

  return (
    <div className="min-h-screen bg-neutral-100 flex items-center justify-center p-6">
      <div className="w-full max-w-md card space-y-6">
        <div className="text-center">
          <p className="text-2xl mb-1">🌿</p>
          <h1 className="text-xl font-bold text-neutral-900">HolistiCare</h1>
          <p className="text-sm text-neutral-500 mt-1">Acceso clínico o diario del paciente</p>
        </div>

        <div className="space-y-3">
          <button
            type="button"
            onClick={handleDevLogin}
            disabled={loading || patientLoading}
            className="btn-primary w-full"
          >
            {loading ? "Conectando…" : "Entrar (desarrollo — clínico)"}
          </button>
          <p className="text-xs text-neutral-400 text-center">
            Requiere <code className="bg-neutral-100 px-1 rounded">ALLOW_DEV_AUTH=true</code> en el API
          </p>
        </div>

        <form onSubmit={handlePatientDevLogin} className="space-y-3 border-t border-neutral-200 pt-4">
          <label htmlFor="patient-uuid-login" className="label">
            UUID de paciente (desarrollo)
          </label>
          <input
            id="patient-uuid-login"
            type="text"
            className="input font-mono text-xs"
            value={patientUuid}
            onChange={(e) => setPatientUuid(e.target.value)}
            placeholder="550e8400-e29b-41d4-a716-446655440000"
            spellCheck={false}
            autoComplete="off"
          />
          <button
            type="submit"
            disabled={loading || patientLoading}
            className="btn-secondary w-full"
          >
            {patientLoading ? "Conectando…" : "Entrar (desarrollo — paciente)"}
          </button>
        </form>

        <div className="relative">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t border-neutral-200" />
          </div>
          <div className="relative flex justify-center text-xs uppercase">
            <span className="bg-white px-2 text-neutral-400">o</span>
          </div>
        </div>

        <form onSubmit={handleManualSubmit} className="space-y-3">
          <label htmlFor="manual-jwt" className="label">
            Pegar token JWT (Bearer)
          </label>
          <textarea
            id="manual-jwt"
            rows={4}
            value={manualToken}
            onChange={(e) => setManualToken(e.target.value)}
            className="input font-mono text-xs"
            placeholder="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            spellCheck={false}
          />
          {error && (
            <p className="text-sm text-red-600" role="alert">
              {error}
            </p>
          )}
          <button type="submit" className="btn-secondary w-full">
            Entrar con token
          </button>
        </form>
      </div>
    </div>
  );
}
