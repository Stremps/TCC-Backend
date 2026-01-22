import { Outlet } from 'react-router-dom';
import { Sidebar } from './Sidebar';

export function MainLayout() {
  return (
    <div className="flex h-screen overflow-hidden bg-gunmetal">
      {/* Sidebar Fixa a Esquerda */}
      <Sidebar />

      {/* Área de Conteúdo (Scrollável) */}
      <main className="flex-1 overflow-y-auto overflow-x-hidden relative">

        
        {/* Onde as páginas (Dashboard, Gallery) serão renderizadas */}
        <div className="relative z-10 min-h-full">
            <Outlet />
        </div>
      </main>
    </div>
  );
}