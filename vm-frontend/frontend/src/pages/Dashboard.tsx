import { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom'; // Para redirecionar futuramente
import { GPUMonitor } from '../components/dashboard/GPUMonitor';
import { InputModeSelector } from '../components/dashboard/InputModeSelector';
import { AdvancedSettings } from '../components/dashboard/AdvancedSettings';
import { useJobSubmit } from '../hooks/useJobSubmit';

export function Dashboard() {
  const navigate = useNavigate();
  
  // --- Estados da Interface ---
  const [mode, setMode] = useState<'TEXT' | 'IMAGE'>('TEXT');
  const [prompt, setPrompt] = useState('');
  
  // Estados - DreamFusion (Text)
  const [steps, setSteps] = useState(1000); // Mínimo seguro
  const [guidance, setGuidance] = useState(7.5);
  const [seed, setSeed] = useState(42);

  // Estados - Stable Fast 3D (Image)
  const [textureRes, setTextureRes] = useState(1024);
  const [remesh, setRemesh] = useState('triangle');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  // Hook de Lógica (O "Cérebro")
  const { submit, isSubmitting, error: submitError } = useJobSubmit();
  const [successMsg, setSuccessMsg] = useState('');

  // Ref para o input de arquivo oculto
  const fileInputRef = useRef<HTMLInputElement>(null);

  // --- Handlers ---

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
       // Validação simples de tipo
       const file = e.dataTransfer.files[0];
       if (file.type.startsWith('image/')) {
         setSelectedFile(file);
       }
    }
  };

  const handleSubmit = async () => {
    setSuccessMsg(''); // Limpa mensagens anteriores
    
    const success = await submit({
      mode,
      prompt,
      steps,
      guidance,
      seed,
      file: selectedFile,
      textureRes,
      remesh
    });

    if (success) {
      setSuccessMsg('Job iniciado com sucesso! Redirecionando para a Galeria...');
      
      // Delay de 2 segundos para o usuário ler a mensagem verde
      setTimeout(() => {
        navigate('/gallery'); // <--- O redirecionamento real agora acontece aqui!
      }, 2000);
    }
  };

  return (
    <div className="flex flex-col min-h-screen">
      
      {/* HEADER */}
      <header className="h-16 bg-gunmetal/95 backdrop-blur sticky top-0 z-10 border-b border-white/5 -mx-8 -mt-8 mb-8 flex items-center shadow-sm">
        <div className="w-full px-12 flex items-center justify-between">
            <h1 className="text-xl font-semibold text-white">Criar Novo Modelo 3D</h1>
            <div className="flex items-center gap-4">
                <GPUMonitor />
            </div>
        </div>
      </header>

      {/* CONTEÚDO */}
      <div className="flex-1 p-8 max-w-5xl mx-auto w-full">
        
        {/* SEÇÃO 1: Escolha */}
        <section className="mb-10">
            <h2 className="text-sm uppercase tracking-wider text-textSec font-semibold mb-4">1. Escolha o Modelo</h2>
            <InputModeSelector mode={mode} onChange={setMode} />
        </section>

        {/* SEÇÃO 2: Entrada de Dados */}
        <section className="mb-8">
            <h2 className="text-sm uppercase tracking-wider text-textSec font-semibold mb-4">2. Entrada de Dados</h2>

            {mode === 'TEXT' && (
                <div id="input-text-container" className="animate-fade-in">
                    <label className="block text-sm text-white mb-2 font-medium">Descreva o objeto:</label>
                    <div className="relative">
                        <textarea 
                            value={prompt}
                            onChange={(e) => setPrompt(e.target.value)}
                            className="w-full h-32 bg-surface border border-white/10 rounded-xl p-4 text-white focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-all resize-none placeholder-textSec/50"
                            placeholder="Ex: Uma cadeira futurista estilo cyberpunk com luzes neon..."
                        ></textarea>
                        <div className="absolute bottom-3 right-3 text-xs text-textSec">{prompt.length}/200</div>
                    </div>
                </div>
            )}

            {mode === 'IMAGE' && (
                <div id="input-image-container" className="animate-fade-in">
                    <label className="block text-sm text-white mb-2 font-medium">Upload da Imagem de Referência:</label>
                    
                    {/* Input Oculto */}
                    <input 
                      type="file" 
                      ref={fileInputRef}
                      onChange={handleFileSelect}
                      accept="image/png, image/jpeg, image/webp"
                      className="hidden"
                    />

                    {/* Área de Clique / Drag & Drop */}
                    <div 
                      onClick={() => fileInputRef.current?.click()}
                      onDragOver={handleDragOver}
                      onDrop={handleDrop}
                      className={`border-2 border-dashed rounded-xl h-48 flex flex-col items-center justify-center cursor-pointer transition-all group ${
                        selectedFile 
                          ? 'border-primary bg-primary/5' 
                          : 'border-white/10 bg-surface/50 hover:border-primary/50 hover:bg-surface'
                      }`}
                    >
                        {selectedFile ? (
                          // Estado: Arquivo Selecionado
                          <>
                             <div className="w-12 h-12 rounded-full bg-primary/20 flex items-center justify-center mb-3 text-primary">
                                <i className="fa-solid fa-check text-xl"></i>
                            </div>
                            <p className="text-sm font-medium text-white">{selectedFile.name}</p>
                            <p className="text-xs text-primary mt-1">Clique para trocar</p>
                          </>
                        ) : (
                          // Estado: Vazio
                          <>
                            <div className="w-12 h-12 rounded-full bg-gunmetal flex items-center justify-center mb-3 group-hover:scale-110 transition-transform">
                                <i className="fa-solid fa-cloud-arrow-up text-primary"></i>
                            </div>
                            <p className="text-sm font-medium text-white">Clique para selecionar ou arraste aqui</p>
                            <p className="text-xs text-textSec mt-1">PNG, JPG ou WEBP (Max 10MB)</p>
                          </>
                        )}
                    </div>
                </div>
            )}
        </section>

        {/* SEÇÃO 3: Configurações Avançadas */}
        <AdvancedSettings 
            mode={mode}
            seed={seed} setSeed={setSeed}
            steps={steps} setSteps={setSteps}
            guidance={guidance} setGuidance={setGuidance}
            textureRes={textureRes} setTextureRes={setTextureRes}
            remesh={remesh} setRemesh={setRemesh}
        />

        {/* Mensagens de Feedback */}
        {submitError && (
          <div className="mb-4 p-4 rounded-lg bg-danger/10 border border-danger/20 text-danger text-sm flex items-center gap-2 animate-shake">
            <i className="fa-solid fa-triangle-exclamation"></i>
            {submitError}
          </div>
        )}
        
        {successMsg && (
          <div className="mb-4 p-4 rounded-lg bg-primary/10 border border-primary/20 text-primary text-sm flex items-center gap-2 animate-fade-in">
            <i className="fa-solid fa-circle-check"></i>
            {successMsg}
          </div>
        )}

        {/* BOTÃO DE AÇÃO */}
        <div className="flex justify-end pt-4 border-t border-white/5">
            <button 
              onClick={handleSubmit}
              disabled={isSubmitting}
              className={`font-bold py-3 px-8 rounded-lg shadow-lg flex items-center gap-2 transition-all ${
                isSubmitting 
                  ? 'bg-surface text-textSec cursor-not-allowed'
                  : 'bg-primary hover:bg-primaryHover text-gunmetal shadow-primary/20 transform active:scale-95'
              }`}
            >
                {isSubmitting ? (
                  <>
                    <i className="fa-solid fa-circle-notch fa-spin"></i>
                    Processando...
                  </>
                ) : (
                  <>
                    <i className="fa-solid fa-cube"></i>
                    Gerar Modelo 3D
                  </>
                )}
            </button>
        </div>

      </div>
    </div>
  );
}