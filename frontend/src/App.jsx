import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import RequireClinician from "./components/RequireClinician";
import RequirePatient from "./components/RequirePatient";
import Layout from "./components/Layout";
import PatientLayout from "./components/PatientLayout";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import PatientDiary from "./pages/PatientDiary";
import PlanReview from "./pages/PlanReview";
import PlanSources from "./pages/PlanSources";
import Chunks from "./pages/Chunks";
import NotFound from "./pages/NotFound";

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          {/* Public routes first — do not nest under Layout (avoids splat catching /login). */}
          <Route path="/login" element={<Login />} />

          {/* US-DIARY-UI-PATIENT — patient self-serve diary */}
          <Route element={<RequirePatient />}>
            <Route element={<PatientLayout />}>
              <Route path="diario" element={<PatientDiary />} />
            </Route>
          </Route>

          <Route element={<RequireClinician />}>
            <Route element={<Layout />}>
              <Route index element={<Navigate to="/dashboard" replace />} />
              <Route path="dashboard" element={<Dashboard />} />
              <Route path="plan/:planId" element={<PlanReview />} />
              <Route path="plan/:planId/sources" element={<PlanSources />} />
              <Route path="chunks" element={<Chunks />} />
              <Route path="*" element={<NotFound />} />
            </Route>
          </Route>
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
