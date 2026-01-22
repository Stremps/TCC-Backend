import { NavLink } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

export function Sidebar() {
  const { signOut, user } = useAuth();

  // Função auxiliar para classes condicionais
  const navClass = ({ isActive }: { isActive: boolean }) => 
    `flex items-center gap-3 rounded-lg px-3 py-2.5 transition-all duration-200 ${
      isActive 
        ? 'bg-primary/10 text-primary font-medium shadow-[inset_3px_0_0_0_#40cf9f]' 
        : 'text-textSec hover:bg-white/5 hover:text-white'
    }`;

  return (
    <aside className="flex h-screen w-64 flex-col border-r border-white/5 bg-surface">
      {/* 1. Logo Area */}
      <div className="flex h-16 items-center border-b border-white/5 px-6">
        <div className="flex items-center ">
            <i className="fa-solid fa-cube text-primary text-xl mr-3"></i>
          <span className="text-lg font-bold text-white tracking-wide">
            Lab<span className="text-primary">CGera</span>
          </span>
        </div>
      </div>

      {/* 2. Navigation Links */}
      <nav className="flex-1 space-y-1 px-3 py-6">
        <div className="px-3 mb-2 text-xs font-semibold uppercase tracking-wider text-textSec/40">
          Principal
        </div>
        
        <NavLink to="/dashboard" className={navClass}>
          <i className="fa-solid fa-wand-magic-sparkles w-5 text-center"></i>
          <span>Nova Geração</span>
        </NavLink>

        <NavLink to="/gallery" className={navClass}>
          <i className="fa-regular fa-folder-open w-5 text-center"></i>
          <span>Minhas Gerações</span>
        </NavLink>
        
        {/* Placeholder para futuras funcionalidades */}
        <div className="mt-8 px-3 mb-2 text-xs font-semibold uppercase tracking-wider text-textSec/40">
          Sistema
        </div>
        <NavLink to="/diagnostic" className={navClass}>
          <i className="fa-solid fa-stethoscope w-5 text-center"></i>
          <span>Diagnóstico</span>
        </NavLink>
      </nav>

      {/* 3. User Profile / Logout */}
      <div className="border-t border-white/5 p-4">
        <div className="flex items-center justify-between rounded-xl bg-gunmetal p-3 border border-white/5">
          <div className="flex items-center gap-3 overflow-hidden">
            <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-white/10 text-xs text-white">
              <i className="fa-solid fa-user"></i>
            </div>
            <div className="flex flex-col truncate">
              <span className="truncate text-sm font-medium text-white">
                {user?.username || 'Usuário'}
              </span>
              <span className="text-[10px] text-textSec">Pesquisador</span>
            </div>
          </div>
          
          <button 
            onClick={signOut}
            className="text-textSec hover:text-danger transition-colors p-1"
            title="Sair"
          >
            <i className="fa-solid fa-right-from-bracket"></i>
          </button>
        </div>
      </div>
    </aside>
  );
}