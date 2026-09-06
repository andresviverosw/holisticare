import { useCallback, useEffect, useRef, useState } from "react";
import { NavLink, Outlet, useLocation, useNavigate } from "react-router";
import { useAuth } from "../context/AuthContext";
import { nextMobileNavOpen } from "../utils/mobileNav";

const navItems = [
  { to: "/dashboard", label: "Dashboard", icon: "🏠" },
  { to: "/chunks", label: "Base de conocimiento", icon: "📚" },
];

function NavItem({ to, label, icon, onNavigate }) {
  return (
    <NavLink
      to={to}
      onClick={onNavigate}
      className={({ isActive }) =>
        `flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
          isActive
            ? "bg-brand-500 text-white"
            : "text-neutral-600 hover:bg-neutral-100"
        }`
      }
    >
      <span aria-hidden>{icon}</span>
      <span>{label}</span>
    </NavLink>
  );
}

function SidebarBody({ onNavigate }) {
  const { role, sub, logout } = useAuth();
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate("/login", { replace: true });
  }

  return (
    <>
      <div className="px-5 py-5 border-b border-neutral-200">
        <div className="flex items-center gap-2">
          <span className="text-2xl" aria-hidden>
            🌿
          </span>
          <div>
            <p className="text-sm font-bold text-neutral-900 leading-none">HolistiCare</p>
            <p className="text-xs text-neutral-400 mt-0.5">Rehab IA</p>
          </div>
        </div>
      </div>

      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto" aria-label="Principal">
        {navItems.map((item) => (
          <NavItem key={item.to} {...item} onNavigate={onNavigate} />
        ))}
      </nav>

      <div className="px-5 py-4 border-t border-neutral-200 space-y-2">
        <p className="text-xs text-neutral-500">
          {role && (
            <>
              <span className="font-medium text-neutral-700">{role}</span>
              {sub && <span className="text-neutral-400"> · {sub}</span>}
            </>
          )}
        </p>
        <button type="button" onClick={handleLogout} className="text-xs text-red-600 hover:underline">
          Cerrar sesión
        </button>
        <p className="text-xs text-neutral-400">v0.1.0 — MVP clínico</p>
      </div>
    </>
  );
}

/** US-MOB-001 — responsive clinician shell: drawer &lt; md, fixed sidebar ≥ md. */
export default function Layout() {
  const [navOpen, setNavOpen] = useState(false);
  const location = useLocation();
  const closeBtnRef = useRef(null);

  const closeNav = useCallback(() => {
    setNavOpen((open) => nextMobileNavOpen({ currentlyOpen: open, forceClosed: true }));
  }, []);

  const toggleNav = useCallback(() => {
    setNavOpen((open) => nextMobileNavOpen({ currentlyOpen: open, toggle: true }));
  }, []);

  useEffect(() => {
    closeNav();
  }, [location.pathname, closeNav]);

  useEffect(() => {
    if (!navOpen) return undefined;
    const onKey = (e) => {
      if (e.key === "Escape") closeNav();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [navOpen, closeNav]);

  useEffect(() => {
    if (navOpen && closeBtnRef.current) {
      closeBtnRef.current.focus();
    }
  }, [navOpen]);

  return (
    <div className="flex h-screen overflow-hidden">
      <aside className="hidden md:flex w-60 flex-shrink-0 bg-white border-r border-neutral-200 flex-col">
        <SidebarBody />
      </aside>

      {navOpen && (
        <div className="fixed inset-0 z-40 md:hidden" role="presentation">
          <button
            type="button"
            className="absolute inset-0 bg-neutral-900/40"
            aria-label="Cerrar menú"
            onClick={closeNav}
          />
          <aside
            id="clinician-mobile-nav"
            className="absolute inset-y-0 left-0 w-[min(16rem,85vw)] max-w-full bg-white border-r border-neutral-200 flex flex-col shadow-lg"
            role="dialog"
            aria-modal="true"
            aria-label="Navegación"
          >
            <div className="flex justify-end px-3 pt-3">
              <button
                ref={closeBtnRef}
                type="button"
                className="text-sm text-neutral-600 px-2 py-1 rounded-lg hover:bg-neutral-100"
                onClick={closeNav}
              >
                Cerrar
              </button>
            </div>
            <SidebarBody onNavigate={closeNav} />
          </aside>
        </div>
      )}

      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        <header className="md:hidden flex items-center gap-3 px-4 py-3 bg-white border-b border-neutral-200 shrink-0">
          <button
            type="button"
            className="inline-flex items-center justify-center rounded-lg border border-neutral-300 px-3 py-2 text-sm font-medium text-neutral-700 hover:bg-neutral-100"
            aria-expanded={navOpen}
            aria-controls="clinician-mobile-nav"
            onClick={toggleNav}
          >
            Menú
          </button>
          <div className="min-w-0">
            <p className="text-sm font-bold text-neutral-900 leading-none truncate">HolistiCare</p>
            <p className="text-xs text-neutral-400 mt-0.5">Rehab IA</p>
          </div>
        </header>

        <main className="flex-1 overflow-y-auto overflow-x-hidden bg-neutral-50 min-w-0">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
