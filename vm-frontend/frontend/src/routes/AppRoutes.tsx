import { Routes, Route, Navigate } from 'react-router-dom';
import { Login } from '../pages/Login';
import { Dashboard } from '../pages/Dashboard';
import { Gallery } from '../pages/Gallery';
import { Diagnostic } from '../pages/Diagnostic';

export function AppRoutes() {
  return (
    <Routes>
      {/* Rota Pública Inicial */}
      <Route path="/" element={<Login />} />

      {/* Rotas que serão Protegidas (Futuramente) */}
      <Route path="/dashboard" element={<Dashboard />} />
      <Route path="/gallery" element={<Gallery />} />
      <Route path="/diagnostic" element={<Diagnostic />} />

      {/* Redirecionamento de rotas desconhecidas para o Login */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}