interface InputModeSelectorProps {
  mode: 'TEXT' | 'IMAGE';
  onChange: (mode: 'TEXT' | 'IMAGE') => void;
}

export function InputModeSelector({ mode, onChange }: InputModeSelectorProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      
      {/* CARD 1: DreamFusion (Texto) */}
      <div 
        onClick={() => onChange('TEXT')} 
        className={`group relative bg-surface border-2 rounded-xl p-6 cursor-pointer hover:bg-surface/80 transition-all ${
          mode === 'TEXT' 
            ? 'border-primary shadow-lg shadow-primary/5' // Estado Ativo
            : 'border-transparent hover:border-white/10'  // Estado Inativo
        }`}
      >
        <div className="absolute top-4 right-4">
          <i className={`text-xl ${
            mode === 'TEXT' 
              ? 'fa-solid fa-circle-check text-primary' 
              : 'fa-regular fa-circle text-textSec'
          }`}></i>
        </div>
        {/* Ícone Azul (Cópia Fiel) */}
        <div className="w-12 h-12 rounded-lg bg-blue-500/10 flex items-center justify-center mb-4 text-blue-400 group-hover:text-blue-300">
            <i className="fa-solid fa-font text-2xl"></i>
        </div>
        <h3 className="text-lg font-bold text-white mb-1">DreamFusion (SD)</h3>
        <p className="text-sm text-textSec">Geração Text-to-3D. Ideal para assets criativos descritos via prompt. Processo iterativo (~5 min).</p>
      </div>

      {/* CARD 2: Stable Fast 3D (Imagem) */}
      <div 
        onClick={() => onChange('IMAGE')} 
        className={`group relative bg-surface border-2 rounded-xl p-6 cursor-pointer hover:bg-surface/80 transition-all ${
          mode === 'IMAGE' 
            ? 'border-primary shadow-lg shadow-primary/5' // Estado Ativo
            : 'border-transparent hover:border-white/10'  // Estado Inativo
        }`}
      >
        <div className="absolute top-4 right-4">
          <i className={`text-xl ${
            mode === 'IMAGE' 
              ? 'fa-solid fa-circle-check text-primary' 
              : 'fa-regular fa-circle text-textSec'
          }`}></i>
        </div>
        {/* Ícone Roxo (Cópia Fiel) */}
        <div className="w-12 h-12 rounded-lg bg-purple-500/10 flex items-center justify-center mb-4 text-purple-400 group-hover:text-purple-300">
            <i className="fa-regular fa-image text-2xl"></i>
        </div>
        <h3 className="text-lg font-bold text-white mb-1">Stable Fast 3D</h3>
        <p className="text-sm text-textSec">Geração Image-to-3D. Transforma uma imagem única em malha 3D. Ultra rápido (&lt; 10s).</p>
      </div>

    </div>
  );
}