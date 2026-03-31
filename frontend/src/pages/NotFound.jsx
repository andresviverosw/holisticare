import { Link } from "react-router-dom";

export default function NotFound() {
  return (
    <div className="flex flex-col items-center justify-center h-full gap-4">
      <p className="text-5xl">🌿</p>
      <h1 className="text-xl font-bold text-neutral-800">Página no encontrada</h1>
      <Link to="/dashboard" className="btn-primary">Volver al inicio</Link>
    </div>
  );
}
