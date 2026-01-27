interface JobCardProps {
    job: {
        id: string;
        model_id: string;
        status: string;
        prompt: string | null;
        created_at: string;
        input_params?: any;
    };
    onDownload: (id: string) => void;
    onView?: () => void; // <--- Nova Prop Opcional
}

export function JobCard({ job, onDownload, onView }: JobCardProps) {
    
    const dateFormatted = new Date(job.created_at).toLocaleDateString('pt-BR', {
        day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit'
    });

    const isTextModel = job.model_id.includes('dreamfusion');
    const title = job.prompt 
        ? (job.prompt.length > 30 ? job.prompt.substring(0, 30) + "..." : job.prompt)
        : "Imagem de Referência";
    
    const description = job.prompt || job.input_params?.input_path?.split('/').pop() || "Modelo 3D gerado via Upload";
    const modelBadge = isTextModel ? 'DFSD' : 'SF3D';

    // 1. STATUS: SUCESSO (Verde)
    if (job.status === 'SUCCEEDED') {
        return (
            <div className="group bg-surface rounded-xl border border-white/5 overflow-hidden hover:border-primary/50 transition-all hover:shadow-lg hover:shadow-primary/5 relative">
                <div className="absolute top-3 left-3 z-10 bg-gunmetal/80 backdrop-blur px-2 py-1 rounded text-xs font-bold text-primary border border-primary/20 flex items-center gap-1">
                    <i className="fa-solid fa-check"></i> PRONTO
                </div>

                <div className="h-48 bg-black/50 relative overflow-hidden cursor-pointer group">
                    <div className="w-full h-full bg-gunmetal flex items-center justify-center">
                         <i className="fa-solid fa-cube text-6xl text-white/5 group-hover:text-primary/20 transition-colors duration-500"></i>
                    </div>
                    
                    {/* Botão Visualizar - Agora funcional! */}
                    <div className="absolute inset-0 bg-primary/10 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center backdrop-blur-[1px]">
                        <button 
                            onClick={onView} // <--- Ação conectada!
                            className="bg-primary text-gunmetal px-4 py-2 rounded-lg font-bold shadow-lg transform translate-y-2 group-hover:translate-y-0 transition-all"
                        >
                            <i className="fa-solid fa-eye mr-1"></i> Visualizar
                        </button>
                    </div>
                </div>

                <div className="p-4">
                    <div className="flex justify-between items-start mb-2">
                        <h3 className="font-semibold text-white truncate pr-2" title={description}>{title}</h3>
                        <span className="text-[10px] text-textSec border border-white/10 px-1.5 rounded bg-gunmetal">{modelBadge}</span>
                    </div>
                    <p className="text-xs text-textSec mb-4 line-clamp-2 h-8">{description}</p>
                    
                    <div className="flex justify-between items-center pt-3 border-t border-white/5">
                        <span className="text-[10px] text-textSec capitalize">{dateFormatted}</span>
                        <div className="flex gap-2">
                            <button 
                                onClick={() => onDownload(job.id)}
                                className="text-textSec hover:text-white transition-colors" 
                                title="Download GLB"
                            >
                                <i className="fa-solid fa-download"></i>
                            </button>
                            <button className="text-textSec hover:text-danger transition-colors" title="Excluir">
                                <i className="fa-regular fa-trash-can"></i>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        );
    }

    // 2. STATUS: PROCESSANDO / NA FILA (Amarelo)
    if (job.status === 'PROCESSING' || job.status === 'QUEUED') {
        return (
            <div className="bg-surface rounded-xl border border-amber-500/30 overflow-hidden relative">
                <div className="absolute top-3 left-3 z-10 bg-gunmetal/80 backdrop-blur px-2 py-1 rounded text-xs font-bold text-amber-500 border border-amber-500/20 flex items-center gap-2">
                    <span className="w-1.5 h-1.5 rounded-full bg-amber-500 animate-pulse"></span> 
                    {job.status === 'QUEUED' ? 'NA FILA' : 'PROCESSANDO'}
                </div>

                <div className="h-48 bg-gunmetal/50 flex flex-col items-center justify-center gap-3">
                    <div className="w-8 h-8 rounded-full border-2 border-amber-500/10 border-l-amber-500 animate-spin"></div>
                    <p className="text-xs text-amber-500 animate-pulse">
                        {job.status === 'QUEUED' ? 'Aguardando Worker...' : 'Gerando Geometria...'}
                    </p>
                </div>

                <div className="p-4 opacity-75">
                    <div className="flex justify-between items-start mb-2">
                        <h3 className="font-semibold text-white truncate pr-2">{title}</h3>
                        <span className="text-[10px] text-textSec border border-white/10 px-1.5 rounded bg-gunmetal">{modelBadge}</span>
                    </div>
                    <p className="text-xs text-textSec mb-4 line-clamp-2 h-8">{description}</p>
                    
                    <div className="w-full bg-gunmetal rounded-full h-1.5 overflow-hidden">
                        <div className="bg-amber-500 h-full rounded-full w-1/3 animate-pulse"></div>
                    </div>
                </div>
            </div>
        );
    }

    // 3. STATUS: FALHA (Vermelho)
    return (
        <div className="bg-surface rounded-xl border border-white/5 overflow-hidden opacity-80 hover:opacity-100 transition-opacity relative">
            <div className="absolute top-3 left-3 z-10 bg-danger/10 px-2 py-1 rounded text-xs font-bold text-danger border border-danger/20 flex items-center gap-1">
                <i className="fa-solid fa-triangle-exclamation"></i> FALHA
            </div>

            <div className="h-48 bg-gunmetal/50 flex flex-col items-center justify-center text-textSec">
                <i className="fa-solid fa-heart-crack text-3xl mb-2 opacity-20"></i>
                <span className="text-xs">Erro na Geração</span>
            </div>

            <div className="p-4">
                <div className="flex justify-between items-start mb-2">
                    <h3 className="font-semibold text-white truncate pr-2">{title}</h3>
                    <span className="text-[10px] text-textSec border border-white/10 px-1.5 rounded bg-gunmetal">{modelBadge}</span>
                </div>
                 <p className="text-xs text-textSec mb-4 line-clamp-2 h-8">Falha técnica.</p>

                <div className="flex justify-between items-center pt-3 border-t border-white/5">
                    <span className="text-[10px] text-textSec capitalize">{dateFormatted}</span>
                    <button className="text-textSec hover:text-white transition-colors text-xs flex items-center gap-1">
                        <i className="fa-solid fa-rotate-right"></i> Tentar de novo
                    </button>
                </div>
            </div>
        </div>
    );
}