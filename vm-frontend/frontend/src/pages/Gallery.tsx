import { useState } from 'react';
import { JobCard } from '../components/gallery/JobCard';
import { ViewerModal } from '../components/gallery/ViewerModal'; // <--- Importamos o componente
import { useJobsPolling } from '../hooks/useJobsPolling';
import { jobsService, type JobRead } from '../services/jobs';

export function Gallery() {
  const [searchTerm, setSearchTerm] = useState('');
  
  // Hook Inteligente
  const { jobs, loading, error } = useJobsPolling();

  // --- ESTADOS PARA O MODAL ---
  const [viewingJob, setViewingJob] = useState<JobRead | null>(null);
  const [modelUrl, setModelUrl] = useState<string | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  // Download
  const handleDownload = async (id: string) => {
    try {
        const downloadUrl = await jobsService.getDownloadUrl(id);
        window.open(downloadUrl, '_blank');
    } catch (err) {
        console.error("Erro no download:", err);
        alert("Não foi possível iniciar o download.");
    }
  };

  // --- NOVA FUNÇÃO: VISUALIZAR ---
  const handleView = async (job: JobRead) => {
      try {
          setViewingJob(job);
          // Reutiliza a lógica de pegar URL assinada (serve tanto pra baixar quanto pra visualizar)
          const url = await jobsService.getDownloadUrl(job.id);
          setModelUrl(url);
          setIsModalOpen(true);
      } catch (err) {
          console.error("Erro ao carregar modelo:", err);
          alert("Erro ao carregar visualização 3D.");
          setViewingJob(null);
      }
  };

  const handleCloseModal = () => {
      setIsModalOpen(false);
      // Limpa os dados após a animação de saída (300ms)
      setTimeout(() => {
          setViewingJob(null);
          setModelUrl(null);
      }, 300);
  };

  // Filtro
  const filteredJobs = jobs.filter(job => {
    const searchLower = searchTerm.toLowerCase();
    const promptMatch = (job.prompt || "").toLowerCase().includes(searchLower);
    const idMatch = job.id.toLowerCase().includes(searchLower);
    const fileMatch = (job.input_params?.input_path || "").toLowerCase().includes(searchLower);
    return promptMatch || idMatch || fileMatch;
  });

  return (
    <div className="flex flex-col min-h-screen">
      
      {/* HEADER */}
      <header className="h-16 bg-gunmetal/95 backdrop-blur sticky top-0 z-10 border-b border-white/5 -mx-8 -mt-8 mb-8 flex items-center shadow-sm">
        <div className="w-full px-12 flex items-center justify-between">
            <h1 className="text-xl font-semibold text-white">Galeria de Modelos</h1>
            <div className="flex gap-2">
                <div className="relative">
                    <i className="fa-solid fa-search absolute left-3 top-2.5 text-textSec text-xs"></i>
                    <input 
                        type="text" 
                        placeholder="Buscar job..." 
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="bg-surface border border-white/10 rounded-full pl-8 pr-4 py-1.5 text-sm text-white focus:border-primary outline-none w-64 placeholder-textSec/50 transition-all focus:w-72"
                    />
                </div>
                <button className="w-8 h-8 rounded-full bg-surface border border-white/10 text-textSec hover:border-primary hover:text-primary flex items-center justify-center transition-colors">
                    <i className="fa-solid fa-filter text-xs"></i>
                </button>
            </div>
        </div>
      </header>

      {/* ÁREA DE CONTEÚDO */}
      <div className="flex-1 px-4 max-w-7xl mx-auto w-full pb-10 pt-10">
         
         {loading && jobs.length === 0 && (
            <div className="flex flex-col items-center justify-center h-64 text-textSec">
                <i className="fa-solid fa-circle-notch fa-spin text-3xl mb-4 text-primary"></i>
                <p>Carregando sua galeria...</p>
            </div>
         )}

         {error && (
            <div className="bg-danger/10 border border-danger/20 text-danger p-4 rounded-xl text-center mb-8">
                <i className="fa-solid fa-triangle-exclamation mr-2"></i>
                {error}
            </div>
         )}

         {!loading && jobs.length === 0 && !error && (
             <div className="flex flex-col items-center justify-center h-96 opacity-50 border-2 border-dashed border-white/5 rounded-2xl">
                <i className="fa-solid fa-box-open text-6xl mb-4 text-textSec"></i>
                <h3 className="text-xl font-semibold text-white">Nenhum modelo criado ainda</h3>
                <p className="text-textSec mt-2">Vá em "Nova Geração" para começar a criar.</p>
             </div>
         )}

         <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {filteredJobs.map(job => (
                <JobCard 
                    key={job.id} 
                    job={job} 
                    onDownload={handleDownload}
                    onView={() => handleView(job)} // <--- Passamos a função aqui
                />
            ))}
         </div>

      </div>

      {/* MODAL GLOBAL (Renderizado fora do grid para sobrepor tudo) */}
      <ViewerModal 
        isOpen={isModalOpen}
        onClose={handleCloseModal}
        modelUrl={modelUrl}
        title={viewingJob?.prompt || viewingJob?.input_params?.input_path || "Modelo 3D"}
        onDownload={() => viewingJob && handleDownload(viewingJob.id)}
      />

    </div>
  );
}