import { Outlet, NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const navItems = [
  { to: "/dashboard", label: "Dashboard", icon: "🏠" },
  { to: "/chunks",    label: "Base de conocimiento", icon: "📚" },
];

function NavItem({ to, label, icon }) {
  return (
    <NavLink
      to={to}
      className={({ isActive }) =>
        `flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
          isActive
            ? "bg-brand-500 text-white"
            : "text-neutral-600 hover:bg-neutral-100"
        }`
      }
    >
      <span>{icon}</span>
      <span>{label}</span>
    </NavLink>
  );
}

export default function Layout() {
  const { role, sub, logout } = useAuth();
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate("/login", { replace: true });
  }

  return (
    <div className="flex h-screen overflow-hidden">
      {/* Sidebar */}
      <aside className="w-60 flex-shrink-0 bg-white border-r border-neutral-200 flex flex-col">
        {/* Logo */}
        <div className="px-5 py-5 border-b border-neutral-200">
          <div className="flex items-center gap-2">
            <span className="text-2xl">🌿</span>
            <div>
              <p className="text-sm font-bold text-neutral-900 leading-none">HolistiCare</p>
              <p className="text-xs text-neutral-400 mt-0.5">Rehab IA</p>
            </div>
          </div>
        </div>

        {/* Nav */}
        <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
          {navItems.map((item) => (
            <NavItem key={item.to} {...item} />
          ))}
        </nav>

        {/* Footer */}
        <div className="px-5 py-4 border-t border-neutral-200 space-y-2">
          <p className="text-xs text-neutral-500">
            {role && (
              <>
                <span className="font-medium text-neutral-700">{role}</span>
                {sub && <span className="text-neutral-400"> · {sub}</span>}
              </>
            )}
          </p>
          <button
            type="button"
            onClick={handleLogout}
            className="text-xs text-red-600 hover:underline"
          >
            Cerrar sesión
          </button>
          <p className="text-xs text-neutral-400">v0.1.0 — MVP clínico</p>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 overflow-y-auto bg-neutral-50">
        <Outlet />
      </main>
    </div>
  );
}
