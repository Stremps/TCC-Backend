import { useState, useEffect, useRef } from 'react';
import { jobsService, type JobRead } from '../services/jobs';

export function useJobsPolling() {
    const [jobs, setJobs] = useState<JobRead[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    // Ref para controlar se o componente está montado (evita set state em unmount)
    const isMounted = useRef(true);

    const fetchJobs = async () => {
        try {
            const data = await jobsService.listJobs();
            if (isMounted.current) {
                setJobs(data);
                setError(null);
            }
        } catch (err) {
            console.error("Erro no polling:", err);
            // Não setamos erro visual no polling para não piscar a tela, 
            // apenas logamos silenciosamente após a primeira carga.
            if (loading && isMounted.current) setError("Falha ao carregar galeria.");
        } finally {
            if (isMounted.current) setLoading(false);
        }
    };

    useEffect(() => {
        isMounted.current = true;

        // 1. Carga Inicial Imediata
        fetchJobs();

        // 2. Configurar Intervalo (Polling a cada 5 segundos)
        const intervalId = setInterval(() => {
            // Opcional: Verificar se a aba está visível antes de chamar
            if (!document.hidden) {
                fetchJobs();
            }
        }, 5000);

        // 3. Cleanup ao desmontar a página
        return () => {
            isMounted.current = false;
            clearInterval(intervalId);
        };
    }, []);

    return { jobs, loading, error };
}