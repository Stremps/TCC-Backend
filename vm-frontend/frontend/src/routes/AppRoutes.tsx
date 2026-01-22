import { Routes, Route, Navigate } from 'react-router-dom';
import { Login } from '../pages/Login';
import { Dashboard } from '../pages/Dashboard';
import { Gallery } from '../pages/Gallery';
import { Diagnostic } from '../pages/Diagnostic';
import { PrivateRoute } from './PrivateRoute';
import { MainLayout } from '../components/layout/MainLayout';

export function AppRoutes() {
  return (
    <Routes>
      {/* Rotas Públicas */}
      <Route path="/" element={<Login />} />

      {/* Rotas Protegidas (Exigem Login + Layout) */}
      <Route element={<PrivateRoute />}>
        <Route element={<MainLayout />}>
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/gallery" element={<Gallery />} />
          <Route path="/diagnostic" element={<Diagnostic />} />
        </Route>
      </Route>

      {/* Fallback */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}