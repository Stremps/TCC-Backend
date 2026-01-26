import { useState } from 'react';

interface AdvancedSettingsProps {
  mode: 'TEXT' | 'IMAGE';
  // Props Genéricas (Shared)
  seed: number;
  setSeed: (val: number) => void;
  // Props DreamFusion (Texto)
  steps: number;
  setSteps: (val: number) => void;
  guidance: number;
  setGuidance: (val: number) => void;
  // Props SF3D (Imagem)
  textureRes: number;
  setTextureRes: (val: number) => void;
  remesh: string;
  setRemesh: (val: string) => void;
}

export function AdvancedSettings({ 
  mode,
  seed, setSeed, 
  steps, setSteps, 
  guidance, setGuidance,
  textureRes, setTextureRes,
  remesh, setRemesh
}: AdvancedSettingsProps) {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <section className="mb-10 bg-surface/30 rounded-xl border border-white/5 overflow-hidden">
      {/* Header do Acordeão */}
      <div 
        onClick={() => setIsOpen(!isOpen)} 
        className="flex items-center justify-between p-4 cursor-pointer hover:bg-white/5 transition-colors select-none"
      >
        <div className="flex items-center gap-2">
            <i className="fa-solid fa-sliders text-primary text-sm"></i>
            <span className="text-sm font-semibold text-white">Configurações Avançadas</span>
        </div>
        <i className={`fa-solid fa-chevron-down text-textSec transition-transform duration-300 ${isOpen ? 'rotate-180 text-primary' : ''}`}></i>
      </div>

      {/* Conteúdo Expansível */}
      <div className={`transition-all duration-300 ease-in-out ${isOpen ? 'max-h-96 opacity-100' : 'max-h-0 opacity-0'}`}>
        <div className="accordion-content bg-gunmetal/30 border-t border-white/5">
          <div className="p-6 grid grid-cols-1 md:grid-cols-2 gap-8">
            
            {/* === CAMPOS DO MODO TEXTO (DreamFusion) === */}
            {mode === 'TEXT' && (
              <>
                {/* Steps */}
                <div>
                    <div className="flex justify-between mb-2">
                        <label className="text-xs font-medium text-textSec">Steps (Qualidade)</label>
                        <span className="text-xs text-primary font-bold">{steps}</span>
                    </div>
                    {/* AJUSTE: Mínimo alterado para 500 conforme solicitado */}
                    <input 
                      type="range" 
                      className="w-full h-1 bg-surface rounded-lg appearance-none cursor-pointer accent-primary" 
                      min="500" max="10000" step="100" 
                      value={steps}
                      onChange={(e) => setSteps(parseInt(e.target.value))}
                    />
                </div>

                {/* Guidance Scale */}
                <div>
                    <div className="flex justify-between mb-2">
                        <label className="text-xs font-medium text-textSec">Guidance Scale (Fidelidade)</label>
                        <span className="text-xs text-primary font-bold">{guidance}</span>
                    </div>
                    <input 
                      type="range" 
                      className="w-full h-1 bg-surface rounded-lg appearance-none cursor-pointer accent-primary" 
                      min="1" max="100" step="0.5" 
                      value={guidance}
                      onChange={(e) => setGuidance(parseFloat(e.target.value))}
                    />
                </div>

                {/* Seed */}
                <div>
                    <label className="text-xs font-medium text-textSec mb-2 block">Seed (Semente Aleatória)</label>
                    <div className="flex gap-2">
                        <input 
                          type="number" 
                          value={seed}
                          onChange={(e) => setSeed(parseInt(e.target.value))}
                          className="flex-1 bg-surface border border-white/10 rounded px-3 py-1 text-sm text-white focus:border-primary outline-none"
                        />
                        <button 
                          type="button"
                          onClick={() => setSeed(Math.floor(Math.random() * 99999))}
                          className="p-2 bg-surface hover:bg-white/10 border border-white/10 rounded text-textSec hover:text-white transition-colors"
                          title="Gerar Aleatório"
                        >
                            <i className="fa-solid fa-dice"></i>
                        </button>
                    </div>
                </div>

                {/* Random BG Toggle (Mock Visual) */}
                <div className="flex items-center justify-between">
                    <label className="text-xs font-medium text-textSec">Fundo Aleatório (Auto)</label>
                    <div className="w-10 h-5 bg-primary rounded-full relative cursor-pointer">
                        <div className="w-3 h-3 bg-white rounded-full absolute top-1 right-1 shadow-sm"></div>
                    </div>
                </div>
              </>
            )}

            {/* === CAMPOS DO MODO IMAGEM (Stable Fast 3D) === */}
            {mode === 'IMAGE' && (
              <>
                 {/* Texture Resolution */}
                 <div>
                    <div className="flex justify-between mb-2">
                        <label className="text-xs font-medium text-textSec">Resolução Textura</label>
                        <span className="text-xs text-primary font-bold">{textureRes}px</span>
                    </div>
                    <select 
                      value={textureRes}
                      onChange={(e) => setTextureRes(parseInt(e.target.value))}
                      className="w-full bg-surface border border-white/10 rounded px-3 py-2 text-sm text-white focus:border-primary outline-none"
                    >
                      <option value="512">512px (Rápido)</option>
                      <option value="1024">1024px (Padrão)</option>
                      <option value="2048">2048px (Alta)</option>
                    </select>
                </div>

                {/* Remesh Option */}
                <div>
                    <div className="flex justify-between mb-2">
                        <label className="text-xs font-medium text-textSec">Remesh (Topologia)</label>
                        <span className="text-xs text-primary font-bold uppercase">{remesh}</span>
                    </div>
                    <select 
                      value={remesh}
                      onChange={(e) => setRemesh(e.target.value)}
                      className="w-full bg-surface border border-white/10 rounded px-3 py-2 text-sm text-white focus:border-primary outline-none"
                    >
                      {/* AJUSTE: Adicionada opção QUAD e descrições mais técnicas */}
                      <option value="none">Nenhum (Original)</option>
                      <option value="triangle">Triangulação (Otimizado)</option>
                      <option value="quad">Quadrangulação (Quad Flow)</option>
                    </select>
                </div>

                {/* Placeholder para manter Grid */}
                <div className="hidden md:block"></div> 
                <div className="hidden md:block"></div> 
              </>
            )}

          </div>
        </div>
      </div>
    </section>
  );
}