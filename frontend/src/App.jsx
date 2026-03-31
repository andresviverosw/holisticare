import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Layout from "./components/Layout";
import Dashboard from "./pages/Dashboard";
import PlanReview from "./pages/PlanReview";
import PlanSources from "./pages/PlanSources";
import Chunks from "./pages/Chunks";
import NotFound from "./pages/NotFound";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="plan/:planId" element={<PlanReview />} />
          <Route path="plan/:planId/sources" element={<PlanSources />} />
          <Route path="chunks" element={<Chunks />} />
          <Route path="*" element={<NotFound />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
