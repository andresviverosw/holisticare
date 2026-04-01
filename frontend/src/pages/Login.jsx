import { useState } from "react";
import { Navigate, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { formatApiError } from "../utils/apiErrors";

export default function Login() {
  const { isAuthenticated, loginDevClinician, loginWithToken } = useAuth();
  const location = useLocation();
  const from = location.state?.from?.pathname || "/dashboard";

  const [manualToken, setManualToken] = useState("");
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  if (isAuthenticated) {
    return <Navigate to={from} replace />;
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
          <p className="text-sm text-neutral-500 mt-1">Acceso para personal clínico</p>
        </div>

        <div className="space-y-3">
          <button
            type="button"
            onClick={handleDevLogin}
            disabled={loading}
            className="btn-primary w-full"
          >
            {loading ? "Conectando…" : "Entrar (desarrollo — clínico)"}
          </button>
          <p className="text-xs text-neutral-400 text-center">
            Requiere <code className="bg-neutral-100 px-1 rounded">ALLOW_DEV_AUTH=true</code> en el API
          </p>
        </div>

        <div className="relative">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t border-neutral-200" />
          </div>
          <div className="relative flex justify-center text-xs uppercase">
            <span className="bg-white px-2 text-neutral-400">o</span>
          </div>
        </div>

        <form onSubmit={handleManualSubmit} className="space-y-3">
          <label className="label">Pegar token JWT (Bearer)</label>
          <textarea
            rows={4}
            value={manualToken}
            onChange={(e) => setManualToken(e.target.value)}
            className="input font-mono text-xs"
            placeholder="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            spellCheck={false}
          />
          {error && <p className="text-sm text-red-600">{error}</p>}
          <button type="submit" className="btn-secondary w-full">
            Entrar con token
          </button>
        </form>
      </div>
    </div>
  );
}
