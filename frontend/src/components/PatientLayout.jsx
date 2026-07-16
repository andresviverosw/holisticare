import { Outlet, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

/** Minimal shell for patient diary — logo + logout only (no clinician nav). */
export default function PatientLayout() {
  const { sub, logout } = useAuth();
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate("/login", { replace: true });
  }

  return (
    <div className="min-h-screen bg-neutral-50 flex flex-col">
      <header className="bg-white border-b border-neutral-200 px-4 py-3 flex items-center justify-between gap-3">
        <div className="flex items-center gap-2 min-w-0">
          <span className="text-xl" aria-hidden>
            🌿
          </span>
          <div className="min-w-0">
            <p className="text-sm font-bold text-neutral-900 leading-none">HolistiCare</p>
            <p className="text-xs text-neutral-400 mt-0.5 truncate">Mi diario</p>
          </div>
        </div>
        <div className="flex items-center gap-3 shrink-0">
          {sub && (
            <p className="text-xs text-neutral-500 hidden sm:block max-w-[12rem] truncate" title={sub}>
              {sub}
            </p>
          )}
          <button type="button" onClick={handleLogout} className="text-xs text-red-600 hover:underline">
            Cerrar sesión
          </button>
        </div>
      </header>
      <main className="flex-1 overflow-y-auto">
        <Outlet />
      </main>
    </div>
  );
}
