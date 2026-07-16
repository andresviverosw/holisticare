import { useEffect, useState } from "react";
import { Navigate, useSearchParams } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { formatApiError } from "../utils/apiErrors";
import { homePathForRole } from "../utils/authRoles";
import { inviteTokenFromSearch } from "../utils/inviteUrl";
import { isValidUuidV4 } from "../utils/uuidV4";

export default function Login() {
  const {
    isAuthenticated,
    role,
    loginWithPassword,
    loginDevClinician,
    loginDevPatient,
    loginWithToken,
    redeemInvite,
  } = useAuth();
  const [searchParams] = useSearchParams();

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [manualToken, setManualToken] = useState("");
  const [patientUuid, setPatientUuid] = useState("");
  const [inviteToken, setInviteToken] = useState(() => inviteTokenFromSearch(searchParams.toString()));
  const [error, setError] = useState(null);
  const [passwordLoading, setPasswordLoading] = useState(false);
  const [loading, setLoading] = useState(false);
  const [patientLoading, setPatientLoading] = useState(false);
  const [inviteLoading, setInviteLoading] = useState(false);
  const [inviteAutoTried, setInviteAutoTried] = useState(false);

  useEffect(() => {
    const fromQuery = inviteTokenFromSearch(searchParams.toString());
    if (fromQuery) setInviteToken(fromQuery);
  }, [searchParams]);

  useEffect(() => {
    if (isAuthenticated || inviteAutoTried) return;
    const fromQuery = inviteTokenFromSearch(searchParams.toString());
    if (!fromQuery) return;
    setInviteAutoTried(true);
    setInviteLoading(true);
    setError(null);
    redeemInvite(fromQuery)
      .catch((err) => {
        setError(
          formatApiError(err, {
            fallback: "No se pudo canjear la invitación (inválida, usada o vencida).",
          }),
        );
      })
      .finally(() => setInviteLoading(false));
  }, [isAuthenticated, inviteAutoTried, redeemInvite, searchParams]);

  if (isAuthenticated) {
    return <Navigate to={homePathForRole(role)} replace />;
  }

  async function handlePasswordLogin(e) {
    e.preventDefault();
    setPasswordLoading(true);
    setError(null);
    try {
      await loginWithPassword(username, password);
    } catch (err) {
      setError(
        formatApiError(err, {
          fallback: err?.message || "Usuario o contraseña incorrectos.",
        }),
      );
    } finally {
      setPasswordLoading(false);
    }
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

  async function handleInviteRedeem(e) {
    e.preventDefault();
    setInviteLoading(true);
    setError(null);
    try {
      await redeemInvite(inviteToken);
    } catch (err) {
      setError(
        formatApiError(err, {
          fallback:
            err?.message || "No se pudo canjear la invitación (inválida, usada o vencida).",
        }),
      );
    } finally {
      setInviteLoading(false);
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

  const busy = passwordLoading || loading || patientLoading || inviteLoading;

  return (
    <div className="min-h-screen bg-neutral-100 flex items-center justify-center p-6">
      <div className="w-full max-w-md card space-y-6">
        <div className="text-center">
          <p className="text-2xl mb-1">🌿</p>
          <h1 className="text-xl font-bold text-neutral-900">HolistiCare</h1>
          <p className="text-sm text-neutral-500 mt-1">Acceso clínico o diario del paciente</p>
        </div>

        <form onSubmit={handlePasswordLogin} className="space-y-3">
          <p className="text-sm font-semibold text-neutral-800">Personal clínico</p>
          <div>
            <label htmlFor="clinician-username" className="label">
              Usuario
            </label>
            <input
              id="clinician-username"
              type="text"
              className="input"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              autoComplete="username"
              spellCheck={false}
            />
          </div>
          <div>
            <label htmlFor="clinician-password" className="label">
              Contraseña
            </label>
            <input
              id="clinician-password"
              type="password"
              className="input"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              autoComplete="current-password"
            />
          </div>
          <button type="submit" disabled={busy} className="btn-primary w-full">
            {passwordLoading ? "Entrando…" : "Entrar"}
          </button>
          <p className="text-xs text-neutral-400 text-center">
            Cuenta creada con <code className="bg-neutral-100 px-1 rounded">seed_clinician.py</code>
          </p>
        </form>

        <form onSubmit={handleInviteRedeem} className="space-y-3 border-t border-neutral-200 pt-4">
          <label htmlFor="invite-token-login" className="label">
            Invitación al diario (paciente)
          </label>
          <input
            id="invite-token-login"
            type="text"
            className="input font-mono text-xs"
            value={inviteToken}
            onChange={(e) => setInviteToken(e.target.value)}
            placeholder="Token del enlace de invitación"
            spellCheck={false}
            autoComplete="off"
          />
          <button type="submit" disabled={busy} className="btn-secondary w-full">
            {inviteLoading ? "Canjeando…" : "Entrar con invitación"}
          </button>
        </form>

        <div className="relative">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t border-neutral-200" />
          </div>
          <div className="relative flex justify-center text-xs uppercase">
            <span className="bg-white px-2 text-neutral-400">desarrollo</span>
          </div>
        </div>

        <div className="space-y-3">
          <button
            type="button"
            onClick={handleDevLogin}
            disabled={busy}
            className="btn-secondary w-full"
          >
            {loading ? "Conectando…" : "Entrar (desarrollo — clínico)"}
          </button>
          <p className="text-xs text-neutral-400 text-center">
            Requiere <code className="bg-neutral-100 px-1 rounded">ALLOW_DEV_AUTH=true</code> en el API
          </p>
        </div>

        <form onSubmit={handlePatientDevLogin} className="space-y-3">
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
          <button type="submit" disabled={busy} className="btn-secondary w-full">
            {patientLoading ? "Conectando…" : "Entrar (desarrollo — paciente)"}
          </button>
        </form>

        <form onSubmit={handleManualSubmit} className="space-y-3 border-t border-neutral-200 pt-4">
          <label htmlFor="manual-jwt" className="label">
            Pegar token JWT (Bearer)
          </label>
          <textarea
            id="manual-jwt"
            rows={3}
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
          <button type="submit" className="btn-secondary w-full" disabled={busy}>
            Entrar con token
          </button>
        </form>
      </div>
    </div>
  );
}
